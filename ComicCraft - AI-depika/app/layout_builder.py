import re


def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    """
    Organizes the generated images and full comic story into a structured layout list.

    Args:
        image_paths (list): List of file paths to generated panel images.
        full_story (str): Complete generated comic story text from Gemini Pro.
        outline (list): List of panel outline dictionaries from Gemini Flash.

    Returns:
        list: A list of panel dictionaries with keys:
              panel, title, image_path, text, scene_description, image_prompt, caption, narration
    """
    # Split the full story into individual panel segments
    # Handle variations: **Panel, ### Panel, or Panel X
    story_panels = []
    if "**Panel" in full_story:
        raw_splits = full_story.split("**Panel")
        story_panels = [f"**Panel{p}" for p in raw_splits if p.strip()]
    elif "### Panel" in full_story:
        raw_splits = full_story.split("### Panel")
        story_panels = [f"Panel{p}" for p in raw_splits if p.strip()]
    else:
        # Fallback split on double newlines
        parts = [p.strip() for p in full_story.split("\n\n") if p.strip()]
        story_panels = parts if len(parts) >= len(outline) else [full_story]

    layout = []
    total_panels = len(outline)

    for idx in range(total_panels):
        panel_info = outline[idx] if idx < len(outline) else {}
        img_path = image_paths[idx] if idx < len(image_paths) else ""

        # Ensure image path has leading slash for web if not present
        web_img_path = img_path.replace("\\", "/")
        if not web_img_path.startswith("/") and not web_img_path.startswith("http"):
            web_img_path = "/" + web_img_path

        # Extract text segment
        if idx < len(story_panels):
            raw_text = story_panels[idx].strip()
            lines = raw_text.splitlines()
            # If the first line is the panel header, drop it for cleaner layout display
            if lines and ("panel" in lines[0].lower() or lines[0].strip().startswith("**")):
                body_text = "\n".join(lines[1:]).strip()
            else:
                body_text = raw_text
        else:
            desc = panel_info.get("scene_description", "")
            body_text = f"**CAPTION:** {desc}\n**NARRATION:** The adventure continues unfolds with dramatic flair."

        # Parse caption and narration for specialized UI displays
        caption_match = re.search(r'\*\*CAPTION:\*\*\s*(.+)', body_text, re.IGNORECASE)
        narration_match = re.search(r'\*\*NARRATION:\*\*\s*(.+)', body_text, re.IGNORECASE)

        caption_text = caption_match.group(1).strip() if caption_match else ""
        narration_text = narration_match.group(1).strip() if narration_match else ""

        panel_title = panel_info.get("title", f"Panel {idx + 1}")
        # Strip any redundant "Panel X:" prefix from title
        clean_title = re.sub(r'^(Panel\s*\d+[:\-]?\s*)', '', panel_title, flags=re.IGNORECASE).strip()
        if not clean_title:
            clean_title = f"Panel {idx + 1}"

        layout.append({
            "panel": idx + 1,
            "title": clean_title,
            "image_path": web_img_path,
            "raw_image_path": img_path,
            "text": body_text,
            "scene_description": panel_info.get("scene_description", ""),
            "image_prompt": panel_info.get("image_prompt", ""),
            "caption": caption_text,
            "narration": narration_text
        })

    return layout
