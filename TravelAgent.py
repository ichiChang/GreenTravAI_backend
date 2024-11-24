from langchain.tools import tool
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.chat_models import ChatOpenAI
import os
from Serp import (
    execute_hotel_query,
    execute_hotel_query_green,
    search_dining,
    search_dining_green,
    search_ticket,
    get_travel_route_with_google_maps,
    get_travel_route_with_google_maps_green,
)
from TravelPlanner import (
    retrieve_document_content,
    retrieve_document_content_green,
    retrieve_document_content_spot,
    retrieve_document_content_spot_green,
)
import datetime


# normal tools
@tool
def hotel_search(query: str, location: str = "Taipei") -> str:
    """
    Tool to search for hotels using SERP API and return titles and links of the results.
    """
    res = execute_hotel_query(query)
    # print(res)
    return res


@tool
def travel_plan_retriever(query: str) -> str:
    """
    Tool to arrange a complete travel plan
    """
    return retrieve_document_content(query)


@tool
def formal_spot_recommanadation_tool(query: str) -> str:
    """
    Tool only for reomnnad formal tourist spot (e.g. 博物館, 公園, 古蹟, 商圈, 大自然景觀)
    """
    return retrieve_document_content_spot(query)


@tool
def dining_and_casual_spot_search(query: str, location: str = "Taipei") -> str:
    """
    Tool to search for dining and casual spot using SERP API and return titles and links of the results.
    """
    print("using dining search")
    res = search_dining(query, location)
    return res


@tool
def ticket_search(query: str, location: str = "Taipei") -> str:
    """
    Tool to search for ticket using SERP API and return titles and links of the results.
    """
    print("using ticket_search")
    res = search_ticket(query, location)
    return res


@tool
def transoprtation_route_search(query: str) -> str:
    """
    Tool to search for ticket using SERP API and return titles and links of the results.
    """
    print("using transoprtation_route_search")
    return get_travel_route_with_google_maps(query)


# green tools


@tool
def travel_plan_retriever_green(query: str) -> str:
    """
    Tool to arrange a complete travel plan
    """
    return retrieve_document_content_green(query)


@tool
def formal_spot_recommanadation_tool_green(query: str) -> str:
    """
    Tool only for reomnnad formal tourist spot (e.g. 博物館, 公園, 古蹟, 商圈, 大自然景觀, 自然保留區, 風景區)
    """
    return retrieve_document_content_spot_green(query)


@tool
def hotel_search_green(query: str, location: str = "Taipei") -> str:
    """
    Tool to search for hotels using SERP API and return titles and links of the results.
    """
    res = execute_hotel_query_green(query)
    # print(res)
    return res


@tool
def dining_and_casual_spot_search_green(query: str, location: str = "Taipei") -> str:
    """
    Tool to search for dining casual spot using SERP API and return titles and links of the results.
    """
    print("using dining search")
    res = search_dining_green(query, location)
    return res


@tool
def transoprtation_route_search_green(query: str) -> str:
    """
    Tool to search for ticket using SERP API and return titles and links of the results.
    """
    print("using transoprtation_route_search")
    return get_travel_route_with_google_maps_green(query)


def run_travel_agent(query: str) -> str:
    print(f' agent init{datetime.datetime.now()}')
    # Define the tools
    tools = [
        Tool(
            name="Hotel information searching tool",
            func=hotel_search,
            description="Use this tool to search for tourist information such as hotel recommandation and general tourist information",
            return_direct=True,
        ),
        Tool(
            name="Travel Planner",
            func=travel_plan_retriever,
            description="Use this tool arrange a complete travel plan or tourist guide",
            return_direct=True,
        ),
        Tool(
            name="formal_spot_recommanadation_tool",
            func=formal_spot_recommanadation_tool,
            description="Use this tool only to give formal spot (e.g. 博物館, 公園, 古蹟, 商圈, 大自然景觀) recommandation",
            return_direct=True,
        ),
        Tool(
            name="dining_and_casual_spot_search",
            func=dining_and_casual_spot_search,
            description="Use this tool to search for dining and casual spot information.",
            return_direct=True,
        ),
        Tool(
            name="Ticket Search",
            func=ticket_search,
            description="Use this tool to search for ticket information and booking information.",
            return_direct=True,
        ),
        Tool(
            name="Transportation Route Search",
            func=transoprtation_route_search,
            description="Use this tool to search for transportation route information.",
            return_direct=True,
        ),
    ]

    # Define the system prompt
    system_prompt = """
System Prompt:
You are a highly knowledgeable agent specializing in travel planning. Your primary functions include providing information about hotels, dining options, and tourist attractions to help users arrange comprehensive travel plans.
The resposne must in JSON format
if the query is not related to travel, tourist, information, please return a short casual chat to user.
only when user talk about 規劃, 安排, then use the Travel Planner

1. **Arranging a Travel Plan:**
    **Indicators:** Queries that include phrases like "規劃旅遊計畫", "安排行程",,"行程" etc.
   - **Tools to Use:**
     - `Travel Planner`: For tourist spot recommendations in a complete travelplan including hotel, spot, restaurant recommendation retrieval and travel plan arrangement.

   - **Usage:**
     - Only When the user requests to arrange or organize a complete travel plan, utilize the above three retriever tools as needed to gather relevant information.
     - Only use the specific retriever tool relevant to the user's request within the context of a travel plan.

2. **Hotel information Offering:**
   - **Tool to Use:**
     - `Hotel information searching tool`: For tourist information such as hotel recommendations, and some genral, non-specific tourist information.
   - **Usage:**
     - When the user's request does not pertain to arranging a complete travel plan but seeks hotel recommendations or information, utilize the `Hotel information searching tool`.
3. **Spot recommandation:**
    **Indicators:** Queries that include phrases like "去哪", "去哪裡","推薦", "有什麼" etc.
   - **Tool to Use:**
     - `formal_spot_recommanadation_tool`: Only for single or serveral formal spot recommandation
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
4. **Dining and casual spot Search and recommendation:**
   - **Tool to Use:**
     - `dining_and_casual_spot_search`: Only for search resturant information or dining stands also for the casual spot recommandation.
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
5. **Ticket Search:**
   - **Tool to Use:**
     - `Ticket Search`: When user asking for booking or searchinga ticket, using ticket search Only for ticket related task
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
6. **Transportation Route Search**
   - **Tool to Use:**
     - `Transportation Route Search`: when user asking for how to go the destination and the route , using this tool
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
7. **Response Style:**
   - 如果tool 主要回傳的是json格式，請直接返回，並要包含所有的資訊
   - When arranging a travel plan, structure the response in a logical sequence in time series (e.g., accommodation first, followed by dining and then spot).
   - if the query is not related to travel, tourist, information, please return a short casual chat to user.

8. **Language:**
   - Respond in the traditioinal Chinese and Must in Json format
"""

    # Initialize the ChatOpenAI with the system prompt
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.2,
        openai_api_key=os.getenv(
            "OPENAI_API_KEY"
        ),  # Securely get your API key from environment variables
    )

    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prefix=system_prompt,
    )

    # Run the agent with the provided query
    print(f' agent work{datetime.datetime.now()}')
    response = agent.run(query)

    return response


# Now you can use the method with your query
# if __name__ == "__main__":
#     query = "請幫我安排台北一日遊的行程，其中想參觀故宮博物院，此外請安排一間Hotel,以及不可重複的的早餐、午餐、晚餐"
#     result = run_travel_agent(query)
#     print(result)


def run_travel_agent_green(query: str) -> str:
    # Define the tools
    tools = [
        Tool(
            name="Hotel information searching tool",
            func=hotel_search_green,
            description="Use this tool to search for tourist information such as hotel recommandation and general tourist information",
            return_direct=True,
        ),
        Tool(
            name="Travel Planner",
            func=travel_plan_retriever_green,
            description="Use this tool arrange a complete travel plan or tourist guide",
            return_direct=True,
        ),
        Tool(
            name="formal_spot_recommanadation_tool",
            func=formal_spot_recommanadation_tool_green,
            description="Use this tool only to give spot recommandation",
            return_direct=True,
        ),
        Tool(
            name="dining_and_casual_spot_search",
            func=dining_and_casual_spot_search_green,
            description="Use this tool to search for dining information.",
            return_direct=True,
        ),
        Tool(
            name="Ticket Search",
            func=ticket_search,
            description="Use this tool to search for ticket information and booking information.",
            return_direct=True,
        ),
        Tool(
            name="Transportation Route Search",
            func=transoprtation_route_search_green,
            description="Use this tool to search for transportation route information.",
            return_direct=True,
        ),
    ]

    # Define the system prompt
    system_prompt = """
System Prompt:
#zh-tw You are a highly knowledgeable agent specializing in travel planning. Your primary functions include providing information about hotels, dining options, and tourist attractions to help users arrange comprehensive travel plans.
The resposne must in JSON format
if the query is not related to travel, tourist, information, please return a short casual chat to user 繁體中文.
only when user talk about 規劃, 安排, then use the Travel Planner

1. **Arranging a Travel Plan:**
    **Indicators:** Queries that include phrases like "規劃旅遊計畫", "安排行程",,"行程" etc.
   - **Tools to Use:**
     - `Travel Planner`: For tourist spot recommendations in a complete travelplan including hotel, spot, restaurant recommendation retrieval and travel plan arrangement.

   - **Usage:**
     - Only When the user requests to arrange or organize a complete travel plan, utilize the above three retriever tools as needed to gather relevant information.
     - Only use the specific retriever tool relevant to the user's request within the context of a travel plan.

2. **Hotel information Offering:**
   - **Tool to Use:**
     - `Hotel information searching tool`: For tourist information such as hotel recommendations, and some genral, non-specific tourist information.
   - **Usage:**
     - When the user's request does not pertain to arranging a complete travel plan but seeks hotel recommendations or information, utilize the `Hotel information searching tool`.
3. **Spot recommandation (formal):**
    **Indicators:** Queries that include phrases like "去哪", "去哪裡","推薦", "有什麼" etc. and the formal spot can meet the requirements
   - **Tool to Use:**
     - `formal_spot_recommanadation_tool`: Only for single or serveral foraml spot recommandation
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
4. **Dining  and casual spot Search and recommendation:**
   - **Tool to Use:**
     - `dining_and_casual_spot_search`: Only for search resturant information or dining stands, also the casual spot that can meet user's requirements
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
5. **Ticket Search:**
   - **Tool to Use:**
     - `Ticket Search`: When user asking for booking or searchinga ticket, using ticket search Only for ticket related task
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
6. **Transportation Route Search**
   - **Tool to Use:**
     - `Transportation Route Search`: when user asking for how to go the destination and the route , using this tool
   - **Usage:**
     - When the user just ask for some spot to go, please just use spot_recommanadation_tool
7. **Response Style:**
   - 如果tool 主要回傳的是json格式，請直接返回，並要包含所有的資訊
   - When arranging a travel plan, structure the response in a logical sequence in time series (e.g., accommodation first, followed by dining and then spot).
   - if the query is not related to travel, tourist, information, please return a short casual chat to user.

8. **Language:**
   - Respond in the traditioinal Chinese **繁體中文** and Must in Json format #zh-tw
"""

    # Initialize the ChatOpenAI with the system prompt
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.2,
        openai_api_key=os.getenv(
            "OPENAI_API_KEY"
        ),  # Securely get your API key from environment variables
    )

    # Initialize the agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prefix=system_prompt,
    )

    # Run the agent with the provided query
    response = agent.run(query)

    return response
