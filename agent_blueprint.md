> **Note:** This document represents the original project plan and architecture. The actual implementation may have evolved during development. Please refer to the current codebase and documentation for the final system design.# Technical Plan: Dynamic Ad Creative Agent

This document outlines the technical plan for building the multi-agent ad generation system.

---

## High-Level Architecture

We will use a hybrid approach that combines Google's Agent Development Kit (ADK) and LangGraph.

* **Google ADK (The "Agent Shell"):** We'll define a single, high-level ADK agent, the `AdCreativeAgent`. This agent is responsible for external communication, exposing methods to start the generation process and retrieve results. This satisfies the use of the hackathon's specified framework.

* **LangGraph (The "Agent Brain"):** The entire six-agent workflow will be implemented as a stateful graph within the `AdCreativeAgent`. LangGraph is ideal for this because our process is a series of well-defined steps where state must be passed and updated. Each of our conceptual "agents" will be a **node** in this graph.

---

## Core Technologies

* **Language:** Python
* **Agent Framework:** Google ADK
* **Workflow Engine:** LangGraph
* **LLM:** Google Gemini (via an API key from Google AI Studio)
* **Image Generation:** An image generation API (e.g., Google Imagen, DALL-E 3)
* **Image Manipulation:** Pillow library
* **UI (for demo):** Streamlit

---

## Data Models & State

We'll define our data structures using Python's `TypedDict` or `Pydantic`. The central piece of our LangGraph implementation will be the `GraphState`.

```python
from typing import TypedDict, List, Optional

class CreativeBrief(TypedDict):
    product_description: str
    target_audience: str
    platform: str # "Facebook", "TikTok", etc.

class AdCopy(TypedDict):
    headline: str
    body: str
    generation_prompt: str

class RawImage(TypedDict):
    image_path: str
    generation_prompt: str

class AdCreative(TypedDict):
    ad_copy: AdCopy
    raw_image: RawImage
    composed_image_path: str
    quality_score: Optional[int]
    performance_metrics: Optional[dict]

# The state that will be passed between nodes in our graph
class GraphState(TypedDict):
    brief: CreativeBrief
    generated_text: List[AdCopy]
    generated_images: List[RawImage]
    composed_ads: List[AdCreative]
    final_recommendation: Optional[str]
```

---

## Agent Implementation as LangGraph Nodes

Each of our agents becomes a Python function that takes the `GraphState` as input and returns a dictionary to update the state.

### 1. Text Generator Node
* **Logic:** The `Text Generator Agent` takes the `CreativeBrief` and uses its internal "strategic intelligence" (likely another LLM call or a set of rules) to craft *multiple, distinct generation prompts*. Each of these prompts is then sent to the Gemini LLM to generate corresponding ad copy variations. The specific `generation_prompt` is stored with each `AdCopy` object for traceability.
* **Pseudocode:**
    ```python
    def generate_text(state: GraphState) -> dict:
    brief = state["brief"]

    # 1. Agent strategizes and creates multiple unique prompts
    strategic_prompts = create_strategic_text_prompts(brief) # Abstracted helper

    # 2. Call LLM for each prompt to generate copy
    generated_copy_list = []
    for prompt in strategic_prompts:
        llm_output = call_gemini_with_prompt(prompt)
        generated_copy_list.append(
            AdCopy(
                headline=llm_output.get("headline", ""),
                body=llm_output.get("body", ""),
                generation_prompt=prompt
            )
        )

    return {"generated_text": generated_copy_list}
    ```

### 2. Image Generator Node
* **Logic:** The `Image Generator Agent` takes the `CreativeBrief` and uses its "visual strategic intelligence" to craft *multiple, distinct generation prompts* optimized for an image generation API. Each prompt is then sent to the chosen image API to produce raw images. The specific `generation_prompt` is stored with each `RawImage` object.
* **Pseudocode:**
    ```python
    def generate_images(state: GraphState) -> dict:
    brief = state["brief"]

    # 1. Agent strategizes and creates multiple unique prompts
    strategic_prompts = create_strategic_image_prompts(brief) # Abstracted helper

    # 2. Call Image API for each prompt to generate an image
    raw_images_list = []
    for prompt in strategic_prompts:
        # This call abstracts the specific API client and saving logic
        image_path = image_api_client.generate(prompt) 

        raw_images_list.append(
            RawImage(
                image_path=image_path,
                generation_prompt=prompt
            )
        )

    return {"generated_images": raw_images_list}
    ```

### 3. Ad Composer Node
* **Logic:** Acts as an AI Art Director. For each raw image and ad copy pair, this agent calls a multimodal LLM (like Gemini Pro Vision) to analyze the image. It asks the LLM to identify the optimal placement (bounding box) and a high-contrast font color for the text. It then parses the LLM's JSON response and uses the Pillow library to execute these intelligent instructions, creating a visually appealing and readable composite ad.
* **Pseudocode:**
    ```python
    from PIL import Image, ImageDraw, ImageFont
    from your_data_models import GraphState, AdCreative

    def compose_ads(state: GraphState) -> dict:
        composed_creatives = []

        for ad_copy, raw_image in zip(state["generated_text"], state["generated_images"]):

            # 1. Get AI-powered placement instructions
            # This helper function hides the complexity of the API call and prompt
            placement_data = get_ai_placement_instructions(raw_image["image_path"])

            # 2. Create the composite image using the instructions
            # This helper function hides the Pillow drawing logic
            new_path = create_composite_image(
                raw_image["image_path"], 
                ad_copy["headline"], 
                placement_data
            )

            # 3. Create the final AdCreative object
            composed_creatives.append(
                AdCreative(
                    ad_copy=ad_copy,
                    raw_image=raw_image,
                    composed_image_path=new_path
                )
            )

        return {"composed_ads": composed_creatives}
    ```

### 4. Evaluator Node
* **Logic:** This agent acts as a quality assurance expert. It loops through the composed ads and calls a multimodal LLM (acting as a marketing expert) to provide a qualitative score based on criteria like clarity, engagement, and alignment with the original CreativeBrief.
* **Pseudocode:**
    ```python
    def evaluate_ads(state: GraphState) -> dict:
        updated_ads = []
        for ad in state["composed_ads"]:
            # Use the final composed image for evaluation
            prompt = f"As a marketing expert, score this ad from 1-10 on clarity, engagement, and alignment with the brief..."
            score = call_multimodal_llm_for_evaluation(prompt, ad['composed_image_path'])
            ad["quality_score"] = score
            updated_ads.append(ad)
        return {"composed_ads": updated_ads}
    ```

### 5. Analytics Node
* **Logic:** This node is triggered in the feedback loop part of the graph. It calls a **mock function** that returns fake performance data.
* **Pseudocode:**
    ```python
    def analyze_performance(state: GraphState) -> dict:
        # For the hackathon, we use a mock function to simulate real data
        mock_data = get_mock_performance_data(len(state["composed_ads"]))
        
        prompt = f"Analyze this performance data and recommend the winner: {mock_data}"
        recommendation = call_gemini_for_analysis(prompt)
        
        return {"final_recommendation": recommendation}
    ```

---

## Building the LangGraph Graph

We will define the workflow and wire the nodes together. The generate_text and generate_images nodes will be set up to run in parallel after the initial brief is received. The compose_ads node will act as a "joiner," only running after both parallel branches have completed.

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(GraphState)

# Add the nodes
workflow.add_node("generate_text", generate_text)
workflow.add_node("generate_images", generate_images)
workflow.add_node("compose_ads", compose_ads)
workflow.add_node("evaluate_ads", evaluate_ads)
workflow.add_node("analyze_performance", analyze_performance)

# Define the edges for parallel execution
workflow.set_entry_point("generate_text")
workflow.set_entry_point("generate_images")

# After text and images are generated, they both lead to the composer node
# LangGraph waits for both inputs before proceeding to compose_ads
workflow.add_edge("generate_text", "compose_ads")
workflow.add_edge("generate_images", "compose_ads")

# The rest of the workflow is sequential
workflow.add_edge("compose_ads", "evaluate_ads")
workflow.add_edge("evaluate_ads", "analyze_performance")
workflow.add_edge("analyze_performance", END)

app = workflow.compile()
```