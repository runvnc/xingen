from ..commands import command
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
import json
from .read_slide import read_slide_content as new_read_slide_content
from .replace_all import slide_replace_all as new_slide_replace_all

# No longer using module-level cache

# The open_presentation function has been removed as it's no longer needed in the stateless approach.

@command()
async def save_presentation(source_filename, destination_filename):
    """Save the presentation to disk, optionally with a new filename.
    Example:
    { "save_presentation": { "source_filename": "original.pptx", "destination_filename": "updated_presentation.pptx" } }
    """
    try:
        prs = Presentation(source_filename)
        prs.save(destination_filename)
        return f"Saved presentation from {source_filename} as {destination_filename}"
    except Exception as e:
        return f"Error saving presentation: {str(e)}"

@command()
async def slide_replace_all(filename, replacements=None, case_sensitive=True, whole_word=False):
    """Replace all occurrences of specified strings in the presentation.
    
    Examples:
    1. Simple text replacement:
    { "slide_replace_all": { "filename": "example.pptx", "replacements": [{"match": "old text", "replace": "new text"}], "case_sensitive": true, "whole_word": false } }
    
    2. Multiple replacements including percentages:
    { "slide_replace_all": { "filename": "example.pptx", "replacements": [
        {"match": "total: 5%", "replace": "total: 10%"},
        {"match": "revenue", "replace": "income"}
      ], 
      "case_sensitive": false, 
      "whole_word": true 
    } }
    
    3. Using regex:
    { "slide_replace_all": { "filename": "example.pptx", "replacements": [
        {"match": "total: \d+%", "replace": "total: 15%", "is_regex": true},
        {"match": "Q[1-4]", "replace": "Quarter ", "is_regex": true}
      ], 
      "case_sensitive": true
    } }
    """
    from .replace_all import slide_replace_all as new_slide_replace_all
    
    if replacements is None:
        return "No replacements provided"

    try:
        prs = Presentation(filename)
        total_replacements = new_slide_replace_all(prs, replacements, case_sensitive, whole_word)
        prs.save(filename)
        return f"Completed {total_replacements} replacements across the presentation and saved to {filename}."
    except Exception as e:
        return f"Error during replacement: {str(e)}"

@command()
async def replace_image(filename, original_image_fname=None, replace_with_image_fname=None):
    """Replace an image in the presentation based on image file names.
    
    Example:
    { "replace_image": { "filename": "presentation.pptx", "original_image_fname": "old_logo.png", "replace_with_image_fname": "/absolute/path/to/new_logo.png" } }
    """
    if original_image_fname is None or replace_with_image_fname is None:
        return "Both original_image_fname and replace_with_image_fname must be provided"

    try:
        prs = Presentation(filename)
        replacements_count = 0

        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                    if shape.image.filename == original_image_fname:
                        im = parts.image.Image.from_file(replace_with_image_fname)

                        slide_part, rId = shape.part, shape._element.blip_rId
                        image_part = slide_part.related_part(rId)
                        image_part.blob = im._blob

                        replacements_count += 1

        prs.save(filename)
        return f"Replaced {replacements_count} instance(s) of {original_image_fname} with {replace_with_image_fname} in {filename}"
    except Exception as e:
        return f"Error replacing image: {str(e)}"


@command()
async def read_slide_content(filename, slide_number):
    """Read and return the content of a slide.
    Example:
    { "read_slide_content": { "filename": "presentation.pptx", "slide_number": 1 } }
    """
    try:
        prs = Presentation(filename)
        content = new_read_slide_content(prs, slide_number)
        return json.dumps(content)
    except Exception as e:
        return json.dumps({"error": str(e)})

@command()
async def update_slide_content(filename, slide_number, content_json):
    """Update a slide with content provided in JSON format.
    For tables, the number of rows in the provided data must match the existing table.
    Example:
    { "update_slide_content": { "filename": "presentation.pptx", "slide_number": 1, "content_json": {"title": "New Title", "subtitle": "New Subtitle", "Table 2": [["Header 1", "Header 2"], ["Row 1 Col 1", "Row 1 Col 2"]]} } }
    """
    try:
        prs = Presentation(filename)
        slide = prs.slides[slide_number - 1]
        content = json.loads(content_json)
        for shape in slide.shapes:
            if shape.name in content:
                if shape.has_text_frame:
                    shape.text_frame.text = content[shape.name]
                elif shape.has_table:
                    if isinstance(content[shape.name], list) and all(isinstance(row, list) for row in content[shape.name]):
                        for i, row in enumerate(content[shape.name]):
                            for j, cell_content in enumerate(row):
                                if i < len(shape.table.rows) and j < len(shape.table.columns):
                                    shape.table.cell(i, j).text = str(cell_content)
                    else:
                        raise ValueError(f"Content for table '{shape.name}' must be a 2D list")
                elif shape.has_chart:
                    if isinstance(content[shape.name], dict) and 'categories' in content[shape.name] and 'values' in content[shape.name]:
                        chart_data = CategoryChartData()
                        chart_data.categories = content[shape.name]['categories']
                        chart_data.add_series('Series 1', content[shape.name]['values'])
                        shape.chart.replace_data(chart_data)
                    else:
                        raise ValueError(f"Content for chart '{shape.name}' must be a dict with 'categories' and 'values' keys")
        prs.save(filename)
        return f"Updated content of slide {slide_number} in {filename}"
    except Exception as e:
        return f"Error updating slide content: {str(e)}"

@command()
async def create_chart(filename, slide_number, chart_type, data, position):
    """Create a chart on the specified slide.
    Example:
    { "create_chart": { "filename": "presentation.pptx", "slide_number": 1, "chart_type": "BAR_CLUSTERED", "data": {"categories": ["A", "B", "C"], "values": [1, 2, 3]}, "position": {"left": 1, "top": 2, "width": 8, "height": 5} } }
    """
    try:
        prs = Presentation(filename)
        slide = prs.slides[slide_number - 1]
        chart_data = CategoryChartData()
        chart_data.categories = data['categories']
        chart_data.add_series('Series 1', data['values'])
        x, y, cx, cy = [Inches(position[key]) for key in ['left', 'top', 'width', 'height']]
        chart = slide.shapes.add_chart(
            getattr(XL_CHART_TYPE, chart_type), x, y, cx, cy, chart_data
        ).chart
        prs.save(filename)
        return f"Created {chart_type} chart on slide {slide_number} in {filename}"
    except Exception as e:
        return f"Error creating chart: {str(e)}"
