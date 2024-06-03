## Inspiration


## What it does


## How we built it

### Teams and Scopes

<!-- Add image from google drive -->
![image](https://drive.google.com/uc?export=view&id=1ns3OuQYeb7_INAuuC-TKIGYnWExhheSx)

We consider there are several teams for customer care support with their respeective scopes of work. The schema of the team looks like this:
    
    ```
    {
        "teams":[
             {
                "teamName": "Warranty and Returns",
                "Members": [
                    "John Doe",
                    "Jane Doe"
                ],
                "Scope": [
                    "If user is not satisfied with the product, then they may ask for a refund or exchange or return",
                    "It checks the warranty of the product and then decides if the product is eligible for return or exchange",
                    "Advise the user on the return and exchange policy",
                    "Tells the user about the procedure to return the product"
                ]
            },
            ...
        ]
    }
    ```

### Agent Builder

![image](https://drive.google.com/uc?export=view&id=1jILGLpavwTFYavw63NEnjwtU-uKCYXVW)

Coming to the Agent Builder Part, firstly we create a `MainChat` agent which analyzes The Customer's Concern and routes to the specialized agent.
It routes the context to these agents:

1. `WarrantyReturns` : This agent is responsible for handling the warranty and returns of the product. It checks the warranty of the product and then decides if the product is eligible for return or exchange. It advises the user on the return and exchange policy and tells the user about the procedure to return the product.

2. `TechnicalIssues`: This agent is responsible for handling the technical issues of the product.

3. `ProductEnquiry`: This agent is responsible for handling the product enquiry of the product. It tells the user about the product details and the availability of the product.

4. `BillingPayment`: This agent is responsible for handling the billing and payment issues of the product. It tells the user about the payment methods and the billing details.

When the user asks a question, the `MainChat` agent analyzes the user's question and routes the context to the specialized agent. The specialized agent then answers the user's question. Each specialized agent has its own scope of work. It tries to answer the user's question based on its scope of work. It resolves the user's query and provides the user with the necessary information. When the chat conversation is over, the flow is handed back to the `MainChat` agent. It asks the user if he/she is satisfied with answer. It sends the `resolution_status` along with `issue_category` and `conversation` to a gcp function.

![image](https://drive.google.com/uc?export=view&id=1qNAHAlF8WtXHgNT44R0zGRVBe5DsYD9f)

Seperately there is `PolicyHelperMain` agent which is responsible for handling the policy and agreement related queries. It tells the user about the company's policies and agreements. 

### Tools

`WarrantyReturns` and `TechnicalIssues` agents asks customer his/her `customer_id` in the beginning of the conversation. This is then passed to `gcp_function` via `customerlogs` tool to fetch the customer's previous logs and activities. This helps the agent to understand the customer's previous issues and provide better support.

`WarrantyReturns` and `TechnicalIssues` agents also uses `similarconv` tool to fetch the conversations from the database which are similar to the current conversation. This helps the agent to understand the past resolutions to the user's query and provide better support. In order to do this tool invokes a gcp function endpoint which runs a 'elastic search' to fetch the similar conversations. We use `cohere` embeddings and use   `qdrant` vector search engine to fetch the similar conversations.


`MainChat` agent uses `sessionend` tool to send the `resolution_status` along with `issue_category` and `conversation` to a gcp function. This helps to keep track of the user's conversation and the resolution status of the conversation.

`PolicyHelperMain` agent uses `policyhelper` tool to fetch the company's policies and agreements from the database. It uses vertex ai agent builder's `Datastores` to store embeddings of chucnks generated from the policies and agreements pdfs.

So the tools are:
- `customerlogs`: Fetches the customer's previous logs and activities. Input is `customer_id`. Output is `Logs`.
- `similarconv`: Fetches the similar conversations from the database. Input is `query`. Output is `Similar Conversations`.
- `sessionend`: Sends the `resolution_status` along with `issue_category` and `conversation` to a gcp function. Returns `Success` if the data is sent successfully.
- `policyhelper`: Fetches the company's policies and agreements from the database. It is built using vertex ai agent builder's `Datastores`.


### Visualization and Dashboard

We store the data when `sessionend` tool is invoked. We maintain a `mongoDB` database to store  `issue_category` and `resolution_status` along with current date and time. This data is then visualized in admin dashboard. The admin dashboard shows the `issue_category` and `resolution_status` of the user's conversation. It also shows the `issue_category` and `resolution_status` of the user's conversation throuch bar and pie charts. 

## Challenges we ran into

1. Seperation of Concerns:
    - Users can ask for a variety of queries. If we try to handle all the queries in a single agent, it will be difficult to manage the conversation. So we need to create specialized agents for each type of query. This will help to manage the conversation better. So we need to create a `MainChat` agent which analyzes the user's query and routes the context to the specialized agent.

2. Handling Repeated Queries:
    - Some queries are repeated by the users. If we try to answer the same query again and again, it will be difficult to manage the conversation. So we need to fetch the similar conversations from the database and provide the user with the past resolutions to the query. This will help the agent to understand the user's query better and provide better support.

3. Better Understanding of Policies and Agreements:
    - Some queries are related to the company's policies and agreements. If we try to answer the query without understanding the policies and agreements, it will be difficult to manage the conversation. So we need to fetch the company's policies and agreements from the database and provide the user with the necessary information. This will help the agent to understand the user's query better and provide better support.


## Accomplishments that we're proud of

1. More Personalized Customer Support:
    - We use `customerlogs` tool to fetch the customer's previous logs and activities. This helps the agent to understand the customer's previous issues and provide better support. 

2. Handling Repeated Queries:
    - We use `similarconv` tool to fetch the conversations from the database which are similar to the current conversation. This helps the agent to understand the past resolutions to the user's query and provide better support.

3. Better Understanding of Policies and Agreements:
    - We use `policyhelper` tool to fetch the company's policies and agreements from the database. It uses vertex ai agent builder's `Datastores` to store embeddings of chucnks generated from the policies and agreements pdfs.

4. Admin Dashboard And Visualization:
    - We visualize the data in admin dashboard. The admin dashboard shows the `issue_category` and `resolution_status` of the user's conversation. It also shows the `issue_category` and `resolution_status` of the user's conversation throuch bar and pie charts. This helps the teams to take better decisions and improve the customer support.


## What we learned


## What's next for Customer grievance
