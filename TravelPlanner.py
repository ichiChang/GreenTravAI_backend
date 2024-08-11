from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore

from langchain import hub
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.runnables import RunnablePassthrough
# from geopy.distance import geodesic
import os
import json

class TravelPlanner:
    def __init__(self, llm_api_key, model="gpt-3.5-turbo-0613"):
        self.llm_api_key = llm_api_key
        self.model = model
        self.llm = ChatOpenAI(temperature=0, model=self.model, openai_api_key=self.llm_api_key)
        self.template = """
        你是一位台北的旅遊專家，根據以下上下文，結合你自己的知識回答問題。
        限制條件：推薦不可重複。
        請用繁體中文回答，並在回答結尾添加“謝謝詢問”。

        {context}

        請將回應格式化為以下JSON格式：
        {{
            "Recommandation": [
              {{
                    "Activity": "住宿",
                    "Location": "住宿名稱",
                    "Address": "住宿地址"
                }},
                {{
                    "Activity": "早餐",
                    "Location": "餐廳名稱",
                    "Address": "餐廳地址"
                }},
                {{
                    "Activity": "景點參觀",
                    "Location": "景點名稱",
                    "Address": "景點地址"
                }},
                {{
                    "Activity": "午餐",
                    "Location": "餐廳名稱",
                    "Address": "餐廳地址"
                }},
                {{
                    "Activity": "景點參觀",
                    "Location": "景點名稱",
                    "Address": "景點地址"
                }},
                {{
                    "Activity": "晚餐",
                    "Location": "餐廳名稱",
                    "Address": "餐廳地址"
                }}
            ],
            "Note": "謝謝詢問"
        }}

        問題: {question}"""
        self.custom_prompt = PromptTemplate.from_template(self.template)

    def json_format(self, response):
        try:
            json_response = json.loads(response)
            return json_response
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def retrieve_document_content_green(self, query):
        print('Retrieving information...')
        
        # Initialize embeddings and vector stores
        embeddings = OpenAIEmbeddings(openai_api_key=self.llm_api_key)
        hotel_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-hotel')
        spot_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-spot')
        gspot_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-gspot')
        ghotel_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-ghotel')
        restaurant_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-restaurant')
        
        # Retrieve documents from each index
        hotel_docs = ghotel_vector_store.as_retriever(search_kwargs={'k': 1,}).get_relevant_documents(query)
        spot_docs = spot_vector_store.as_retriever(search_kwargs={'k': 1,}).get_relevant_documents(query)
        gspot_docs = gspot_vector_store.as_retriever(search_kwargs={'k': 1,}).get_relevant_documents(query)
        restaurant_docs = restaurant_vector_store.as_retriever(search_kwargs={'k': 3,}).get_relevant_documents(query)

        # Format documents
        context = (
            "Hotel: "+self.format_docs(hotel_docs) + "\n\n" + 
            self.format_docs(spot_docs) + "\n\n" + 
            "餐廳：" + self.format_docs(restaurant_docs)+"\n\n"+
            "綠色景點："+self.format_docs(gspot_docs)
            
        )

        # Combine context with the question
        final_prompt = self.custom_prompt.format(context=context, question=query)

        # Invoke the LLM chain
        result = self.llm(final_prompt)

        # Parse the result
        json_response = self.json_format(result.content)

        return json_response


    def retrieve_document_content(self, query):
        print('Retrieving information...')
        
        # Initialize embeddings and vector stores
        embeddings = OpenAIEmbeddings(openai_api_key=self.llm_api_key)
        hotel_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-hotel')
        spot_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-spot')
        restaurant_vector_store = PineconeVectorStore(embedding=embeddings, index_name='travel-agent-restaurant')

        # Retrieve documents from each index
        hotel_docs = hotel_vector_store.as_retriever(search_kwargs={'k': 1}).get_relevant_documents(query)
        spot_docs = spot_vector_store.as_retriever(search_kwargs={'k': 1}).get_relevant_documents(query)
        restaurant_docs = restaurant_vector_store.as_retriever(search_kwargs={'k': 3}).get_relevant_documents(query)

        # Format documents
        context = (
            "Hotel: "+self.format_docs(hotel_docs) + "\n\n" + 
            self.format_docs(spot_docs) + "\n\n" + 
            "餐廳：" + self.format_docs(restaurant_docs)
        )

        # Combine context with the question
        final_prompt = self.custom_prompt.format(context=context, question=query)

        # Invoke the LLM chain
        result = self.llm(final_prompt)

        # Parse the result
        json_response = self.json_format(result.content)

        return json_response


