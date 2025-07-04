import requests
from bs4 import BeautifulSoup
import re
from string import punctuation

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

from exceptions import TranslationException

class Text:
    def __init__(self, language: str, title: str = None, content: str = None):
        self.language = language
        self.title = title
        self.content = content

    def get(self, url: str):
        COLONPATTERN = re.compile(r':\s$', re.MULTILINE)
        
        # Text pattern that indicates where to stop content extraction
        STOP_TEXT = "मुख्य पृष्ठ :"

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        headings = soup.find_all('h1')
        paragraphs = soup.find_all('p')

        # Get title from the first heading
        if headings:
            self.title = headings[0].get_text().split(":")[0].strip()
        
        if paragraphs:
            all_paragraphs = []
            for p in paragraphs:
                text = p.get_text().replace("दु:", "दु").replace("छ:", "छह")
                text = re.sub(COLONPATTERN, '-', text)

                if STOP_TEXT in text:
                    break
                
                if text.strip():  # Only add non-empty paragraphs
                    all_paragraphs.append(text.strip())
            
            
            self.content = " ".join(all_paragraphs)

    def translate(self, to_language: str, llm):
        if not self.content:
            raise TranslationException(
                "Content is missing. Please fetch the content first.",
                source_lang=self.language,
                target_lang=to_language
            )

        translation_template = '''
        Act as highly proficient translator for {from_lang} and {to_lang} languages.
        Between tags <TEXT> and </TEXT>, is text of a popular story for kids in {from_lang} language. Please translate it to {to_lang} language.

        Only return the translation in {to_lang} language, nothing else. Do not embed the translation in <TEXT> and </TEXT> tags.

        Returned text must be personalised, highly engaging and suitable for a youtube channel highly popular amongst kids of 5 years to 14 years.
        
        Return ONLY the translation. e.g. \"वन में एक बंदर निवास करता था, जो वन के फल आदि खा कर अपना निर्वाह करता था\" is translated to \"In the forest lived a clever monkey who loved to munch on yummy fruits!\"
        and not \"Hey kids, gather around for an amazing story! In the forest lived a clever monkey who loved to munch on yummy fruits!\"

        <TEXT>{text}</TEXT>
        '''

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3300, chunk_overlap=10, length_function=len, separators=['\n', '।\s$'])
        chunks = text_splitter.split_text(text=self.content)

        text_prompt = PromptTemplate(template=translation_template, input_variables=['from_lang', 'to_lang', 'text'])
        chain = LLMChain(llm=llm, prompt=text_prompt)

        translated_text = []
        try:
            for chunk in chunks:
                input = {'from_lang': self.language, 'to_lang': to_language, 'text': chunk}
                translated_text.append(chain.run(input))
        except Exception as e:
            raise TranslationException(
                f"Translation failed: {str(e)}",
                source_lang=self.language,
                target_lang=to_language,
                details={"error": str(e), "chunk_count": len(chunks)}
            )

        return " ".join(translated_text)