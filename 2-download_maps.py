import requests
import time
import pandas as pd
import os
import pprint
import re



##### SET SEARCH URL, FILETYPE, AND SAVE LOCATION #####

searchURL = 'https://www.loc.gov/collections/sanborn-maps/?fa=location:rhode+island%7Clocation:block+island'
fileExtension = 'jpg'
saveTo = 'input/'




'''Run P1 search and get a list of results.'''
def get_item_ids(url, items=[], conditional='True`'):
    # Check that the query URL is not an item or resource link.
    exclude = ["loc.gov/item","loc.gov/resource"]
    if any(string in url for string in exclude):
        raise NameError('Your URL points directly to an item or '
                        'resource page (you can tell because "item" '
                        'or "resource" is in the URL). Please use '
                        'a search URL instead. For example, instead '
                        'of \"https://www.loc.gov/item/2009581123/\", '
                        'try \"https://www.loc.gov/maps/?q=2009581123\". ')

    # request pages of 100 results at a time
    params = {"fo": "json", "c": 100, "at": "results,pagination"}
    call = requests.get(url, params=params)
    # Check that the API request was successful
    if (call.status_code==200) & ('json' in call.headers.get('content-type')):
        data = call.json()
        results = data['results']
        for result in results:
            # Filter out anything that's a colletion or web page
            filter_out = ("collection" in result.get("original_format")) \
                    and ("web page" in result.get("original_format")) \
                    and (eval(conditional)==False)
            if not filter_out:
                # Get the link to the item record
                if result.get("id"):
                    item = result.get("id")
                    # Filter out links to Catalog or other platforms
                    if item.startswith("http://www.loc.gov/item"):
                        items.append(item)
        # Repeat the loop on the next page, unless we're on the last page.
        if data["pagination"]["next"] is not None:
            next_url = data["pagination"]["next"]
            get_item_ids(next_url, items, conditional)

        return items
    else:
            print('There was a problem. Try running the cell again, or check your searchURL.')


'''Get a list of image URLs from those results
If an item has 2+ copies/pages, all copies/pages
are included. User selects file format (e.g., tiff).'''
def get_image_urls(id_list, mimetype, items = []):
    print('Generating a list of files to download . . . ')
    #Standardize any spelling varieties supplied by user.
    if mimetype == 'tif':
        mimetype = 'tiff'
    if mimetype == 'jpg':
        mimetype = 'jpeg'
    params = {"fo": "json"}
    for item in id_list:
        call = requests.get(item, params=params)
        if call.status_code == 200:
            data = call.json()
        elif call.status_code == 429:
            print('Too many requests to API. Stopping early.')
            break
        else:
            try:
                time.sleep(15)
                call = requests.get(item, params=params)
                data = call.json()
            except:
                print('Skipping: '+ item)
                continue
        resources = data['resources']
        for resource_index,resource in enumerate(resources):
            resource_url = data['item']['resources'][resource_index]['url']
            for index,file in enumerate(resource['files']):
                image_df = pd.DataFrame(file)

                if mimetype == 'pdf':
                    full_mimetype = 'application/' + mimetype
                else:
                    full_mimetype = 'image/' + mimetype
                selected_format_df = image_df[
                    image_df['mimetype']==full_mimetype
                ]
                try:
                    last_selected_format = selected_format_df.iloc[-1]['url']
                    file_info = {}
                    file_info['image_url'] = last_selected_format
                    file_info['item_id'] = item
                    items.append(file_info)
                except:
                    print('Note: No ' + mimetype +
                          ' files found in '+
                          resource_url + '?sp=' + str(index+1))
        #Pause between requests

    print('\nFound '+str(len(id_list))+' items')
    print('Found '+str(len(items))+' files to download')
    return items


'''Download all the image URLs'''
def get_image_files(image_urls_list, path):
    image_urls_df = pd.DataFrame(image_urls_list)
    for index, row in image_urls_df.iterrows():
        image_url = row['image_url']
        item_id = row['item_id']
        print('Downloading: '+ image_url)
        try:
            #filename = create a filename based on the last part of the URL.
            #directory = create a folder based on the item ID.
            id_prefix = item_id.split('/')[-2]
            directory = path + id_prefix + '/'
            if os.path.isdir(directory)==False:
                os.makedirs(directory)
            #IIIf URLs (jpegs) need to be parsed in a special way
            if 'image-services/iiif' in image_url:
                #split the url by "/"
                url_parts = image_url.split('/')
                #find the section that begins "service:"
                regex = re.compile("service:.*")
                pointer = list(filter(regex.match, url_parts))
                #split that section by ":".The last part will be the filename.
                filename = pointer[0].split(':')[-1]
                #get the file extension
                ext = image_url.split('.')[-1]
                filename = filename + '.' + ext
            #non-IIIF URLs are simpler
            else:
                filename = image_url.split('/')[-1]
            filepath = os.path.join(directory, filename)
            print('Saving as: ' + filepath)
            #request the image and write to path
            image_response = requests.get(image_url, stream=True)
            with open(filepath, 'wb') as fd:
                for chunk in image_response.iter_content(chunk_size=100000):
                    fd.write(chunk)
        except ConnectionError as e:
            print(e)
        #Pause between downloads
        # time.sleep(6)




# 1. get_item_ids
ids = get_item_ids(searchURL, items=[])

# 2. get_image_urls
image_urls_list = get_image_urls(ids, fileExtension, items=[])

print('\nList of files to be downloaded:')
for url in image_urls_list:
 print(url['image_url'])

# 3. get_image_files
get_image_files(image_urls_list,saveTo)
