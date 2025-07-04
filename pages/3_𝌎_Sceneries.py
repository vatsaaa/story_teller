import json, os, re
import streamlit as st

from utils.Utils import MULTISPACE
from exceptions import ConfigurationException, ImageGenerationException

st.title("Get Sceneries Description")

if st.session_state.get('story'):
    story = st.session_state.get('story', None)

    # Check if sceneries exist and are not empty
    if hasattr(story, 'sceneries') and story.sceneries:
        with st.form(key='sceneries_form'):
            st.subheader("Scenery Titles and Explanations")

            # Display sceneries if they exist
            for key, value in story.sceneries.items():
                st.markdown(f"**{key.strip()}**")
                
                # Description text area
                description = value.get("description", "") if isinstance(value, dict) else str(value)
                st.text_area(
                    label="Description", 
                    height=80, 
                    value=re.sub(MULTISPACE, ' ', description), 
                    key=f"desc_{key.strip()}",
                    label_visibility="collapsed"
                )
                
                # Adjectives text area
                adjectives = value.get("adjectives", []) if isinstance(value, dict) else []
                adjectives_str = ", ".join(adjectives) if isinstance(adjectives, list) else str(adjectives)
                st.text_area(
                    label="Sentiments", 
                    height=70, 
                    value=adjectives_str, 
                    key=f"adj_{key.strip()}"
                )
                
                st.divider()  # Add a visual separator between sceneries
                
            submit_sceneries = st.form_submit_button(label='Generate Sceneries', help='Click to generate images based on the edited sceneries')
            if submit_sceneries:
                # Update sceneries with edited values
                for key in story.sceneries.keys():
                    # Get edited description
                    edited_description = st.session_state.get(f"desc_{key.strip()}", "")
                    
                    # Get edited adjectives and convert back to list
                    edited_adjectives_str = st.session_state.get(f"adj_{key.strip()}", "")
                    edited_adjectives = [adj.strip() for adj in edited_adjectives_str.split(",") if adj.strip()]
                    
                    # Update the sceneries dictionary
                    if isinstance(story.sceneries[key], dict):
                        story.sceneries[key]["description"] = edited_description
                        story.sceneries[key]["adjectives"] = edited_adjectives
                    else:
                        # Convert to dict format if it wasn't already
                        story.sceneries[key] = {
                            "description": edited_description,
                            "adjectives": edited_adjectives
                        }
                
                try:
                    story.get_images()
                    st.session_state['story'] = story
                    st.success("Images generated successfully!")
                except ConfigurationException as e:
                    st.error("🔧 **Configuration Error**")
                    st.info(f"""
                    **{str(e)}**
                    
                    **To fix this:**
                    1. Add the missing configuration to your `.env` file
                    2. Restart the application after adding the configuration
                    
                    For now, you can continue to the Audio and Video pages without images.
                    """)
                except ImageGenerationException as e:
                    st.error("🖼️ **Image Generation Failed**")
                    st.warning(f"Error details: {str(e)}")
                    st.info("You can try again or continue to the next steps without images.")
                except Exception as e:
                    st.error(f"❌ **Unexpected Error**: {str(e)}")
                    st.info("Please try again or continue to the next steps.")
    else:
        st.warning("Sceneries not generated yet. Please go to the English page and generate sceneries first.")
else:
    st.warning("No story found. Please go to the Home page and fetch a story first.")
