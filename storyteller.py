import google.generativeai as genai
import PIL.Image

genai.configure(api_key="AIzaSyA42-u7_ut2DhE4nt5bmqs7l5JO_Ond5ME")

# Use Gemini 1.5 Flash - it's the best for hackathons (fast and handles images)
model = genai.GenerativeModel('gemini-1.5-flash')

# Load your monument image
img = PIL.Image.open('tajmahal.jpg')

# The prompt for HeritageAI
prompt = "Identify this monument and tell me its history in 3 points using Hinglish. Also suggest one famous food nearby."

response = model.generate_content([prompt, img])

print("-" * 30)
print(response.text)
print("-" * 30)