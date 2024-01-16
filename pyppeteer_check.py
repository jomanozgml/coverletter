from pyppeteer import launch

async def get_details_indeed(givenUrl):
    # browser = await launch(args= ['--no-sandbox']) #Downloads the browser
    # browser = await launch({'headless': False})
    browser = await launch(executablePath = './588429/chrome-win32/chrome.exe', args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

    if 'indeed' in givenUrl and 'jk' in givenUrl:
      jkValue = givenUrl.split('jk=')[1].split('&')[0]
      baseUrl = 'https://au.indeed.com/viewjob?jk='
      url = baseUrl + jkValue
    else:
      url = givenUrl

    await page.goto(url)
    pageTitle = await page.title()

    async def get_value(tagName):
      tag = await page.querySelector(tagName)
      tagText = await page.evaluate('(element) => element.innerText', tag) if tag else ""
      return tagText

    try:
      if 'indeed' in givenUrl:
        position = await get_value('h1')
        company = await get_value('[data-company-name = "true"]')
        salary = await get_value('#salaryInfoAndJobType')
        details = await get_value('#jobDescriptionText')

      elif 'careerjet' in givenUrl:
        position = await get_value('h1')
        company = await get_value('.company')
        salary = await get_value('.details')
        details = await get_value('.content')

      elif 'careerone' in givenUrl:
        position = await get_value('h1')
        company = await get_value('.jv-subtitle')
        salary = await get_value('.jv-pay-summary')
        details = await get_value('#jvDescription')

      elif 'jora' in givenUrl:
        position = await get_value('.job-title.heading-xxlarge')
        company = await get_value('.company')
        # location = await get_value('.location')
        salary = await get_value('.badge.-default-badge')
        details = await get_value('#job-description-container')

      elif 'glassdoor' in givenUrl:
        position = await get_value('[data-test="job-title"]')
        #location = await get_value('[data-test="location"]')
        company = await get_value('[data-test="employer-name"]')
        salary = await get_value('.small.css-10zcshf.e1v3ed7e1')
        details = await get_value('#JobDescriptionContainer')

      descriptionText = [position, company, salary, details]
    except:
      pTags = await page.querySelectorAll('p, h1, h2, h3, ul')
      descriptionText = [await page.evaluate('(element) => element.innerText', p) for p in pTags]

    await browser.close()
    print('extracted using pyppeteer')
    return pageTitle, descriptionText