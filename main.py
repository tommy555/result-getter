"""
Impport required library
"""
from bs4 import BeautifulSoup
import requests
import urllib
import urllib3


# Variable
HTML_PROTOCOL = "http://portal7.utar.edu.my/"
TARGET_URL = HTML_PROTOCOL+"loginPage.jsp"
LOGIN_ID = "1800528"
LOGIN_PASS = "960804-01-6509"
LOCATION_TEXT = "location.href='"

# methods

def getRedirectURL(text):
    # Get data from portal page
    soup = BeautifulSoup(text, "html.parser")
    text = soup.find("script").text

    # get redirect URL from the string
    start_pos = text.find(LOCATION_TEXT)+len(LOCATION_TEXT)
    end_pos = len(text)-1
    redirect_url = text[start_pos:end_pos] 
    return redirect_url

def run():
    """ run the main proccess"""
    form_url = ""
    print("Loading website....")
    while True:
        # get login page
        s = requests.Session()
        login_page = s.get(url=TARGET_URL, verify=False)

        """ Making decision on status code """
        if str(login_page.status_code)[0] == '2':
            # proceed to next step if status code return success

            # Using bs lib to organize result content
            soup = BeautifulSoup(login_page.text, "html.parser")

            # try to find the form url for futher proccess
            for e in soup.find_all(attrs={"name":"loginForm"}):
                # if the taken object is not empty, store the object data and break the loop
                tmp_url = e.get("action")
                if tmp_url != "":
                    form_url = HTML_PROTOCOL+tmp_url
                    break
            
            # Print out information and start login into portal
            print(
                "\n\n\nSending request and data to {}\nID: {}\nPassword: {}\n\n\nLoading content...."
                .format(
                    form_url,
                    LOGIN_ID,
                    LOGIN_PASS
                    ))
            portal_page = s.post(form_url, verify=False, data={
                "UserName":LOGIN_ID,
                "Password":LOGIN_PASS
            })

            """ Check request status """
            if str(portal_page.status_code)[0] == '2':
                # Get data from portal page    
                # start redirect URL
                portal_page_2 = s.get(getRedirectURL(portal_page.text), verify=False)

                """ Check request status """
                if str(portal_page_2.status_code)[0] == '2':
                    # get second redirect URL
                    result_page = s.get(getRedirectURL(portal_page_2.text), verify=False)
                    if str(result_page.status_code)[0] == '2':
                        result_page_2 = s.get(HTML_PROTOCOL+"intranet/index.jsp", verify=False)

                        # check if result already released
                        if result_page_2.text.find("You are not authorised to view this page.") != -1:
                            f = open("result.htm", "w")
                            f.write(result_page_2.text)
                            f.close()
                            s.close()
                            print("\n\n\n\nObtain data success!!")
                            break
                    else:
                        # return error message
                        print("Unable to get responses from {}. status code: {}"
                        .format(result_page, result_page.status_code))
                        s.close()
                else:
                    # return error message
                    print("Unable to get responses from {}. status code: {}"
                    .format(portal_page_2, portal_page_2.status_code))
                    s.close()
            else:
                # Return error message
                print("Unable to get responses from {}. status code: {}"
                .format(portal_page, portal_page.status_code))
                s.close()
        else:
            # return error message if fail
            print("Unable to get the content. Code: {}".format(login_page.status_code))
            s.close()

# Main proccess
if __name__ == "__main__":
    run()
