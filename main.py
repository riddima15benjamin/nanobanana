from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import base64
import uvicorn

# ------------------------------
# Configure Gemini API
# ------------------------------
genai.configure(api_key="AIzaSyAn6X7NcjUDmA5BITkZI2gczVXAGiYkkss")  # replace with your real key

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ------------------------------
# Step 1: Business details
# ------------------------------
@app.get("/", response_class=HTMLResponse)
def step1(request: Request):
    return templates.TemplateResponse("step1_logo.html", {"request": request})

# ------------------------------
# Step 2: Campaign Objective
# ------------------------------
@app.post("/objective", response_class=HTMLResponse)
async def step2(request: Request, 
                business_details: str = Form(...),
                logo: UploadFile = File(None)):
    logo_data = ""
    logo_type = ""
    if logo and logo.filename:
        logo_bytes = await logo.read()
        logo_data = base64.b64encode(logo_bytes).decode('utf-8')
        logo_type = logo.content_type
    
    return templates.TemplateResponse("step2_objective.html", {
        "request": request,
        "business_details": business_details,
        "logo_data": logo_data,
        "logo_type": logo_type
    })

# ------------------------------
# Step 3: Marketing Channel
# ------------------------------
@app.post("/channel", response_class=HTMLResponse)
def step3(request: Request,
          business_details: str = Form(...),
          campaign_objective: str = Form(...),
          logo_data: str = Form(""),
          logo_type: str = Form("")):
    return templates.TemplateResponse("step3_channel.html", {
        "request": request,
        "business_details": business_details,
        "campaign_objective": campaign_objective,
        "logo_data": logo_data,
        "logo_type": logo_type
    })

# ------------------------------
# Step 4: Promotional Focus
# ------------------------------
@app.post("/focus", response_class=HTMLResponse)
def step4(request: Request,
          business_details: str = Form(...),
          campaign_objective: str = Form(...),
          marketing_channel: str = Form(...),
          logo_data: str = Form(""),
          logo_type: str = Form("")):
    return templates.TemplateResponse("step4_focus.html", {
        "request": request,
        "business_details": business_details,
        "campaign_objective": campaign_objective,
        "marketing_channel": marketing_channel,
        "logo_data": logo_data,
        "logo_type": logo_type
    })

# ------------------------------
# Step 5: Extra Images Upload
# ------------------------------
@app.post("/images", response_class=HTMLResponse)
def step5(request: Request,
          business_details: str = Form(...),
          campaign_objective: str = Form(...),
          marketing_channel: str = Form(...),
          promotional_focus: str = Form(...),
          logo_data: str = Form(""),
          logo_type: str = Form("")):
    return templates.TemplateResponse("step5_images.html", {
        "request": request,
        "business_details": business_details,
        "campaign_objective": campaign_objective,
        "marketing_channel": marketing_channel,
        "promotional_focus": promotional_focus,
        "logo_data": logo_data,
        "logo_type": logo_type
    })

# ------------------------------
# Final Generate
# ------------------------------
@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    business_details: str = Form(...),
    campaign_objective: str = Form(...),
    marketing_channel: str = Form(...),
    promotional_focus: str = Form(...),
    logo_data: str = Form(""),
    logo_type: str = Form(""),
    extra_images: list[UploadFile] = File(None)
):

    og_prompt = f"""
    You are a professional marketing AI agent that creates visual content descriptions for businesses.

CRITICAL: Before processing any request, verify that all user-provided information is spelled correctly. Accuracy in brand representation is essential.

TASK: Create detailed, actionable design briefs for 3 marketing assets. Focus on providing comprehensive visual descriptions that a designer could use to create pixel-perfect images.

When a user provides their business details, Campaign Objective, Marketing Channel, and Promotional Focus, analyze their industry, target demographic, and business type to automatically determine the most appropriate color scheme, aesthetic style, and design approach.

INPUT PARAMETERS:
Business Details: {business_details}
Campaign Objective: {campaign_objective}
Marketing Channel: {marketing_channel}
Promotional Focus: {promotional_focus}

DESIGN FRAMEWORK: Industry-Based Design Guidelines: - 
Tech/Software: Clean blues (#2563EB, #64748B), whites (#FFFFFF) with modern minimalist aesthetic - 
Beauty/Cosmetics: Soft pastels (#F8BBD0, #E8B4CB), rose gold (#E8B4B8), champagne (#F7E7CE) with elegant touches - 
Food/Restaurant: Warm earth tones (#D97706, #DC2626), appetite-appealing imagery with organic shapes - 
Finance/Banking: Deep blues (#1E40AF, #065F46), grays (#6B7280) with trustworthy, professional feel - 
Health/Medical: Clean whites (#FFFFFF), medical blues (#3B82F6), greens (#10B981) with sterile aesthetic - 
Fashion/Retail: Demographic-adaptive palettes (bold for Gen-Z, sophisticated for millennials) - 
Fitness/Sports: Energetic oranges (#EA580C), reds (#DC2626), blacks (#000000) with dynamic design - 
Education: Friendly blues (#3B82F6), greens (#059669), yellows (#F59E0B) with approachable feel Demographic-Based Adjustments: - 
Gen-Z (16-26): Bold gradients, neon accents (#00D9FF, #FF006E), trendy fonts, high contrast - 
Millennials (27-42): Instagram-worthy pastels, clean lines, modern serif/sans-serif combinations - 
Gen-X (43-58): Classic color combinations, highly readable fonts, professional layouts - 
Baby Boomers (59+): Traditional colors, clear typography, simplified compositions CHANNEL-

SPECIFIC OUTPUT: Based on Marketing Channel: {marketing_channel}, for the  marketing channel selected, generate 3 distinct, minimal, 
and aesthetically pleasing marketing assets.
CRITICAL: Make sure the marketing assets have the correct dimensions for the given marketing channel. Guidelines for the dimensions are provided below.

**If Social Media is selected:** 
1. Instagram Post (1080x1080px) 
2. Instagram Story (1080x1920px) 
3. Facebook Cover (1200x630px) 

**If Digital Advertising is selected:** 
1. Google Display Ad (728x90px) 
2. Social Media Ad (1080x1080px) 
3. Banner Ad (320x50px - Mobile) 

**If Email Marketing is selected:** 
1. Email Header (600x200px) 
2. Email Newsletter Banner (600x300px) 
3. Email Signature Banner (400x100px) 

**If Print Materials is selected:** 
1. Poster Design (18x24 inches) 
2. Flyer Design (8.5x11 inches) 
3. Business Card (3.5x2 inches) 

**If Website/Landing Page is selected:** 
1. Hero Banner (1920x600px) 
2. CTA Section Banner (1200x400px) 
3. Sidebar Ad (300x250px) 

QUALITY STANDARDS: - Ensure all text is legible at specified dimensions 
- Maintain brand consistency across all three formats 
- Optimize for conversion based on marketing channel 
- Consider accessibility (contrast ratios, readability) 
- Include mobile-responsive considerations for digital formats

Do not output reasoning or text — only images.
    """

    # Prepare inputs
    base_inputs = [{"text": og_prompt}]
    logo_preview_html = ""
    extra_preview_html = ""

    if logo_data and logo_type:
        try:
            logo_bytes = base64.b64decode(logo_data)
            base_inputs.append({"mime_type": logo_type, "data": logo_bytes})
            logo_preview_html = f"<h3>Uploaded Logo:</h3><img src='data:{logo_type};base64,{logo_data}' width='200'><br>"
        except Exception as e:
            print(f"Error processing logo: {e}")
            logo_preview_html = "<p>Logo uploaded but could not be processed.</p>"

    if extra_images:
        for img in extra_images:
            img_bytes = await img.read()
            if img_bytes:
                base_inputs.append({"mime_type": img.content_type, "data": img_bytes})
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")
                extra_preview_html += f"<img src='data:{img.content_type};base64,{img_b64}' width='200' style='margin:5px;'>"

    # Generate 3 images (loop)
    parts_html = []
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash-image-preview")

        for i in range(3):  # call 3 times
            response = model.generate_content(base_inputs)

            if response.candidates and len(response.candidates) > 0:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        img_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type
                        img_b64 = base64.b64encode(img_data).decode("utf-8")
                        parts_html.append(
                            f"<div style='margin:10px;'><img src='data:{mime_type};base64,{img_b64}' width='400'></div>"
                        )

        if not parts_html:
            parts_html.append("<p>No images generated. Try again.</p>")
        
        output_html = "".join(parts_html)

    except Exception as e:
        output_html = f"<div style='color:red;'><h3>Error generating images:</h3><p>{str(e)}</p></div>"

    return templates.TemplateResponse("generate.html", {
        "request": request,
        "logo_preview_html": logo_preview_html,
        "extra_preview_html": extra_preview_html,
        "output_html": output_html
    })

# ------------------------------
# Run App
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

