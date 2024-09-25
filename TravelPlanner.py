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


def json_format(response):
    try:
        json_response = json.loads(response)
        return json_response
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}
def get_retriever(category_type, index_name, top_k):
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('LLM_API_KEY'))
    dynamic_filter = {"type": category_type}

    # Create the retriever
    retriever = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings,
        text_key="Name"
    )

    # Set the filter and top_k
    retriever = retriever.as_retriever(
        search_kwargs={
            "filter": dynamic_filter,
            "k": top_k  # Do not include 'include_metadata'
        }
    )
    return retriever

def format_docs_with_metadata(docs):
    # Format both the content and metadata for each document
    formatted_docs = []
    for doc in docs:
        metadata = doc.metadata  # Metadata field from each document
        content = doc.page_content  # The actual content of the document
        formatted_docs.append(f"Content: {content}\nMetadata: {metadata}")

    return "\n\n".join(formatted_docs)

def retrieve_document_content(query):
    print('Retrieving information...')

    llm = ChatOpenAI(temperature=0, model="gpt-4o", openai_api_key=os.getenv('LLM_API_KEY'))

    # Define the template
    template = """你是一位台北的旅遊專家，根據以下上下文，結合你自己的知識回答問題。
                  限制條件：推薦不可重複。
                  請用繁體中文回答，並在回答結尾NOTE添加 SHORT SUMMARY。
                  回答中請勿包含```json
                  



                  {context}

                  請將回應格式化為符合以下JSON格式的plain text：
                  {{"Recommandation": [
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
                      "Note": SHORT SUMMARY
                  }}

                  問題: {question}"""

    custom_prompt = PromptTemplate.from_template(template)

    # Retrieve documents from each index
    hotel_retriever = get_retriever('normal', 'travel-agent-hotel', top_k=1)
    hotel_docs = hotel_retriever.get_relevant_documents(query)

    spot_retriever = get_retriever('normal', 'travel-agent-spot', top_k=2)
    spot_docs = spot_retriever.get_relevant_documents(query)

    restaurant_retriever = get_retriever('normal', 'travel-agent-restaurant', top_k=3)
    restaurant_docs = restaurant_retriever.get_relevant_documents(query)

    # Format documents with metadata
    context = format_docs_with_metadata(hotel_docs) + "\n\n" + \
              format_docs_with_metadata(spot_docs) + "\n\n" + \
              "餐廳：" + format_docs_with_metadata(restaurant_docs)

    # Combine context with the question
    final_prompt = custom_prompt.format(context=context, question=query)

    # print(final_prompt)

    # Invoke the LLM chain
    result = llm.invoke(final_prompt)
    # print(result.content)
    # Parse the result
    json_response = json_format(result.content)

    return json_response


def retrieve_document_content_green(query):
    print('Retrieving information...')

    llm = ChatOpenAI(temperature=0, model="gpt-4o", openai_api_key=os.getenv('LLM_API_KEY'))

    # Define the template
    template = """你是一位台北的旅遊專家，根據以下上下文，結合你自己的知識回答問題。
                  限制條件：推薦不可重複。
                  請用繁體中文回答，並在回答結尾NOTE添加 SHORT SUMMARY。
                  回答中請勿包含```json
                  



                  {context}

                  請將回應格式化為符合以下JSON格式的plain text：
                  {{"Recommandation": [
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
                      "Note": SHORT SUMMARY
                  }}

                  問題: {question}"""

    custom_prompt = PromptTemplate.from_template(template)

    # Retrieve documents from each index
    hotel_retriever = get_retriever('green', 'travel-agent-hotel', top_k=1)
    hotel_docs = hotel_retriever.get_relevant_documents(query)

    spot_retriever = get_retriever('green', 'travel-agent-spot', top_k=2)
    spot_docs = spot_retriever.get_relevant_documents(query)

    restaurant_retriever = get_retriever('green', 'travel-agent-restaurant', top_k=3)
    restaurant_docs = restaurant_retriever.get_relevant_documents(query)

    # Format documents with metadata
    context = format_docs_with_metadata(hotel_docs) + "\n\n" + \
              format_docs_with_metadata(spot_docs) + "\n\n" + \
              "餐廳：" + format_docs_with_metadata(restaurant_docs)

    # Combine context with the question
    final_prompt = custom_prompt.format(context=context, question=query)

    # print(final_prompt)

    # Invoke the LLM chain
    result = llm.invoke(final_prompt)
    # print(result.content)
    # Parse the result
    json_response = json_format(result.content)

    return json_response