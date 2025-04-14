import streamlit as st
import google.generativeai as genai
from datetime import datetime
import time
import random


def main():
    st.set_page_config(page_title="Advanced Prompt Generator", layout="wide")

    # Check if API key is already set
    if 'api_key_set' not in st.session_state:
        st.session_state.api_key_set = False
    if 'api_working' not in st.session_state:
        st.session_state.api_working = False

    if not st.session_state.api_key_set:
        api_key_page()
    else:
        prompt_generator_page()


def api_key_page():
    st.title("Welcome to Advanced Prompt Generator")
    st.write("Please enter your Google API Key to get started.")

    api_key = st.text_input("Enter your Google API Key", type="password")
    if st.button("Submit"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Test the API key
                model = genai.GenerativeModel('gemini-pro')
                model.generate_content("Test")
                st.session_state.api_key = api_key
                st.session_state.api_key_set = True
                st.session_state.api_working = True
                st.success("API Key verified successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error verifying API Key: {str(e)}")
                st.info("You can still use the app with fallback functionality.")
                if st.button("Continue with Fallback Mode"):
                    st.session_state.api_key_set = True
                    st.session_state.api_working = False
                    st.rerun()
        else:
            st.warning("Please enter an API Key or continue with fallback functionality.")
            if st.button("Continue with Fallback Mode"):
                st.session_state.api_key_set = True
                st.session_state.api_working = False
                st.rerun()


def prompt_generator_page():
    st.title("Advanced Prompt Generator")

    if not st.session_state.api_working:
        st.warning("Running in Fallback Mode. Some features may be limited.")

    # Initialize session state
    if 'generated_prompts' not in st.session_state:
        st.session_state.generated_prompts = []
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []

    # Sidebar for advanced options and previously generated prompts
    with st.sidebar:
        st.title("Advanced Options")
        target_audience = st.selectbox("Target Audience",
                                       ["General", "Professionals", "Students", "Researchers", "Creatives"])
        industry = st.selectbox("Industry",
                                ["Technology", "Healthcare", "Finance", "Education", "Entertainment", "Other"])

        # Prompt template library
        templates = {
            "SWOT Analysis": "Generate a SWOT analysis for {theme} in the {industry} industry.",
            "Product Description": "Write a compelling product description for {theme} targeting {target_audience}.",
            "Research Question": "Formulate a research question about {theme} for {target_audience} in the {industry} sector."
        }
        selected_template = st.selectbox("Prompt Template", ["Custom"] + list(templates.keys()))

        st.title("Previously Generated Prompts")
        display_previous_prompts()

    # Main content area with tabs
    tab1, tab2 = st.tabs(["Generate New Prompt", "Favorite Prompts"])

    with tab1:
        st.subheader("Generate New Prompt")
        if selected_template == "Custom":
            theme = st.text_input("Enter prompt theme or keywords:", key="theme")
        else:
            theme = st.text_input("Enter specific topic for the template:", key="theme")

        tone = st.selectbox("Select tone:", ["Formal", "Creative", "Technical", "Casual", "Professional"], key="tone")
        complexity = st.multiselect("Select complexity:", ["Short", "Medium", "Long"], default=["Medium"],
                                    key="complexity")

        if st.button("Generate Prompt", key="generate"):
            if st.session_state.api_working:
                generate_prompt_api(theme, tone, complexity, target_audience, industry, selected_template, templates)
            else:
                generate_prompt_fallback(theme, tone, complexity, target_audience, industry, selected_template,
                                         templates)

    with tab2:
        st.subheader("Favorite Prompts")
        display_favorite_prompts()

    # Combine prompts
    st.subheader("Combine Prompts")
    combine_prompts()

    # Clear button
    if st.button("Clear All"):
        clear_all()


def generate_prompt_api(theme, tone, complexity, target_audience, industry, selected_template, templates):
    if theme:
        try:
            # Prepare the input for Gemini
            if selected_template == "Custom":
                input_prompt = f"Generate an AI prompt with the following parameters:\nTheme: {theme}\nTone: {tone}\nComplexity: {', '.join(complexity)}\nTarget Audience: {target_audience}\nIndustry: {industry}\n\nGenerated Prompt:"
            else:
                template = templates[selected_template].format(theme=theme, target_audience=target_audience,
                                                               industry=industry)
                input_prompt = f"Generate an AI prompt based on the following template:\n{template}\nTone: {tone}\nComplexity: {', '.join(complexity)}\n\nGenerated Prompt:"

            # Generate the prompt using Gemini
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(input_prompt)
            generated_prompt = response.text

            # Display the generated prompt
            st.subheader("Generated Prompt:")
            st.write(generated_prompt)

            # Word count estimator
            word_count = len(generated_prompt.split())
            st.write(f"Estimated word count: {word_count}")

            # Add to session state
            st.session_state.generated_prompts.append({"text": generated_prompt, "rating": 3})

            # Export functionality
            if st.button("Export Prompt"):
                export_prompt(generated_prompt)

            # Rate limiting
            time.sleep(1)  # Simple rate limiting
        except Exception as e:
            st.error(f"An error occurred while generating the prompt: {str(e)}")
            st.info("Switching to fallback method.")
            st.session_state.api_working = False
            generate_prompt_fallback(theme, tone, complexity, target_audience, industry, selected_template, templates)
    else:
        st.warning("Please enter a theme or keywords.")


def generate_prompt_fallback(theme, tone, complexity, target_audience, industry, selected_template, templates):
    if theme:
        fallback_prompt = create_fallback_prompt(theme, tone, complexity, target_audience, industry, selected_template,
                                                 templates)
        st.subheader("Generated Prompt (Fallback Mode):")
        st.write(fallback_prompt)

        # Word count estimator
        word_count = len(fallback_prompt.split())
        st.write(f"Estimated word count: {word_count}")

        # Add to session state
        st.session_state.generated_prompts.append({"text": fallback_prompt, "rating": 3})

        # Export functionality
        if st.button("Export Prompt"):
            export_prompt(fallback_prompt)
    else:
        st.warning("Please enter a theme or keywords.")


def create_fallback_prompt(theme, tone, complexity, target_audience, industry, selected_template, templates):
    prompt_starters = [
        "Create a",
        "Develop a",
        "Design a",
        "Craft a",
        "Compose a",
    ]

    tone_phrases = {
        "Formal": "professional and structured",
        "Creative": "imaginative and original",
        "Technical": "detailed and precise",
        "Casual": "relaxed and conversational",
        "Professional": "polished and business-oriented"
    }

    complexity_phrases = {
        "Short": "concise",
        "Medium": "moderately detailed",
        "Long": "comprehensive"
    }

    if selected_template == "Custom":
        starter = random.choice(prompt_starters)
        tone_phrase = tone_phrases[tone]
        complexity_phrase = " and ".join([complexity_phrases[c] for c in complexity])
        return f"{starter} {complexity_phrase} {tone_phrase} prompt about {theme} for {target_audience} in the {industry} industry."
    else:
        template = templates[selected_template].format(theme=theme, target_audience=target_audience, industry=industry)
        tone_phrase = tone_phrases[tone]
        complexity_phrase = " and ".join([complexity_phrases[c] for c in complexity])
        return f"{template} Make it {complexity_phrase} and {tone_phrase}."


def display_previous_prompts():
    for i, prompt in enumerate(st.session_state.generated_prompts[-5:]):
        with st.expander(f"Prompt {i + 1}"):
            st.write(prompt['text'])
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Favorite", key=f"fav_{i}"):
                    if prompt not in st.session_state.favorites:
                        st.session_state.favorites.append(prompt)
            with col2:
                new_rating = st.number_input(f"Rate", min_value=1, max_value=5, value=prompt['rating'], key=f"rate_{i}")
                if new_rating != prompt['rating']:
                    prompt['rating'] = new_rating


def display_favorite_prompts():
    if not st.session_state.favorites:
        st.write("No favorite prompts yet. Start favoriting prompts to see them here!")
    else:
        for i, prompt in enumerate(st.session_state.favorites):
            with st.expander(f"Favorite {i + 1}"):
                st.write(prompt['text'])
                if st.button(f"Remove from Favorites", key=f"remove_fav_{i}"):
                    st.session_state.favorites.remove(prompt)
                    st.rerun()


def combine_prompts():
    selected_prompts = st.multiselect("Select prompts to combine", range(len(st.session_state.generated_prompts)))
    if st.button("Combine Selected Prompts"):
        combined_prompt = " ".join([st.session_state.generated_prompts[i]['text'] for i in selected_prompts])
        st.text_area("Combined Prompt", combined_prompt, height=200)


def export_prompt(prompt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_prompt_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(prompt)
    st.success(f"Prompt exported as {filename}")


def clear_all():
    for key in ['theme', 'tone', 'complexity']:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.generated_prompts = []
    st.session_state.favorites = []
    st.rerun()


if __name__ == "__main__":
    main()