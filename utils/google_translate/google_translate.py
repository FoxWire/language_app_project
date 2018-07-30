'''
This works, I am able to translate the sentence with the key. I don't know why though. I had to download some 
other stuff, that I don't seem to need like the json file. There is also a software library that you can download 
for python, I don't know what the advantage of that is though. I also had to set bash variabels and it doesn't seem
to have been necessary.

keep an eye on this billing page to see if the amount goes down at all:
https://console.developers.google.com/billing/017E4D-DA0D96-FDAF9A?project=my-project-1530368023639
'''

import os
import requests
import json
from language_app_project.settings import BASE_DIR


class Translator:

    def __init__(self):
        self.url = 'https://translation.googleapis.com/language/translate/v2'
        self.target_language = 'de'
        self.api_key = self._get_api_key()
        self.cache_file = os.path.join(BASE_DIR, 'utils/google_translate/translation_cache.json')
        self.characters_translated, self.characters_saved = self._get_character_data()

    def _get_api_key(self):

        path = os.path.join(BASE_DIR, 'utils/google_translate/api.key')
        with open(path) as key:
            return key.readline().strip()

    def get_translation(self, chunk):

        # check that the translation has not already been done.
        result = self._check_cache(chunk)
        if result:
            # print("***  INFO: Translation retrieved from cache   ***")
            self.characters_saved += len(chunk)
            self._update_character_data()
            return result

        else:
            # make the api call
            data = {'q': chunk, 'target': self.target_language, 'key': self.api_key}
            response = requests.post(self.url, data=data)
            data = json.loads(response.text)
            translations = data['data']['translations']
            print("***   INFO: Translation made via API call   ***")
            self.characters_translated += len(chunk)
            self._update_character_data()

            if len(translations) > 1:
                print("***   INFO: More than one translation returned for this chunk: {}  ***".format(chunk))
                for translation in translations:
                    print("\t***   {}   ***".format(translation))
            else:
                translated_chunk = translations[0]['translatedText']
                self._write_to_cache(chunk, translated_chunk)
                return translated_chunk

    def get_cache(self):
        with open(self.cache_file) as data_file:
            return json.loads(data_file.read())

    def _get_character_data(self):
        with open(self.cache_file) as data_file:
            cache = json.loads(data_file.read())

            translated = cache.get('characters_translated')
            if not translated:
                translated = 0

            saved = cache.get('characters_saved')
            if not saved:
                saved = 0

            return translated, saved

    def _update_character_data(self):

        # Read from the cache file
        with open(self.cache_file) as data_file:
            cache = json.loads(data_file.read())

            # Add the new entry to the cache
            cache['characters_translated'] = self.characters_translated
            cache['characters_saved'] = self.characters_saved

        # write to the cache file again
        with open(self.cache_file, 'w') as cache_file:
            json.dump(cache, cache_file, indent=4)

    def _check_cache(self, chunk):

        # Read from the cache file
        with open(self.cache_file) as data_file:
            cache = json.loads(data_file.read())

            return cache.get(chunk)

    def _write_to_cache(self, chunk, translation):

        # Read from the cache file
        with open(self.cache_file) as data_file:
            cache = json.loads(data_file.read())

            # Add the new entry to the cache
            cache[chunk] = translation

        # write to the cache file again
        with open(self.cache_file, 'w') as cache_file:
            json.dump(cache, cache_file, indent=4)


if __name__ == '__main__':
    t = Translator()
    chunk = "It's going to be time for another cigarette soon."
    translation = t.get_translation(chunk)
    translation = translation.encode('utf-8')
    print(translation)
	

