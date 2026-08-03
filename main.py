from graph.graph import graph
from langchain_core.messages import HumanMessage

config = {
    "configurable": {
        "thread_id": "1"
    }
}

while True:
    question = input("You: ")

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ]
        },
        config=config
    )

    print("\n" + "=" * 80)
    print(result["final_itinerary"])

    print("✅ PDF Generated Successfully")

    print("Saved as Voyage_AI_Itinerary.pdf")






