import openai
class Summarizer:
    
    def __init__(self, api_key) -> None:
        self.api_key= api_key
        self.MSG_HEADER = 'summarize messages: '

    def summarize(self, pages) -> str:
        msg = ' '.join(pages)
        openai.api_key = self.api_key
        try:
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": self.MSG_HEADER + msg}])
            return completion.choices[0].message['content']
        except Exception as e:
            print(e)
            return 'Something wrong while generating summary...'



if __name__ == '__main__':
    api_key = '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'
    test_summarizer = Summarizer(api_key)
    msg = test_summarizer.summarize(['Weve developed usage guidelines that help developers understand and address potential safety issues.', 'We recognize that bias is a problem that manifests at the intersection of a system and a deployed context; applications built with our technology are sociotechnical systems, so we work with our developers to ensure theyre putting in appropriate processes and human-in-the-loop systems to monitor for adverse behavior.'])
    print(msg)