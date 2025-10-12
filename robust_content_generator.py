import requests
from bs4 import BeautifulSoup
import urllib.parse
from transformers import pipeline, set_seed
import textwrap
import warnings
from PIL import Image
from io import BytesIO
import os
import random
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

warnings.filterwarnings('ignore')


class RobustContentGenerator:
    def __init__(self):
        set_seed(datetime.now().microsecond)
        self.summarizer = self._safe_load_model("summarization", "facebook/bart-large-cnn")
        self.story_gen = self._safe_load_model("text-generation", "gpt2-medium")

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _safe_load_model(self, task, model_name):
        try:
            return pipeline(task, model=model_name)
        except Exception as e:
            print(f"⚠️ Could not load {model_name}: {str(e)}")
            return None

    def generate_content(self, prompt, content_type="summary"):
        try:
            if content_type == "summary":
                return self._generate_summary(prompt)
            elif content_type == "story":
                return self._generate_story(prompt)
            else:
                return {"error": "Invalid content type"}
        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}

    def _generate_summary(self, topic):
        try:
            content = self._fetch_web_content(topic) or f"Provide a detailed summary about {topic}."

            if self.summarizer is None:
                summary_text = self._fallback_summary(topic)
            else:
                summary_text = self._summarize_with_paragraphs(content, 400)

            image_path = self._fetch_image(topic, "infographic")

            result = {
                'type': 'summary',
                'topic': topic,
                'content': summary_text,
                'image': image_path,
                'word_count': len(summary_text.split())
            }

            self._save_pdf(result)

            return result
        except Exception as e:
            return {"error": f"Summary generation failed: {str(e)}"}

    def _generate_story(self, prompt):
        try:
            if self.story_gen is None:
                story = self._fallback_story(prompt)
            else:
                story = self._generate_story_with_paragraphs(prompt, 600)

            image_path = self._fetch_image(prompt, "art")

            result = {
                'type': 'story',
                'title': prompt,
                'content': story,
                'image': image_path,
                'word_count': len(story.split())
            }

            self._save_pdf(result)

            return result
        except Exception as e:
            return {"error": f"Story generation failed: {str(e)}"}

    def _summarize_with_paragraphs(self, text, word_count):
        try:
            if len(text.split()) < 50:
                text = f"{text} " * 10

            summary = self.summarizer(
                text[:10000],
                max_length=word_count+50,
                min_length=max(100, word_count-100),
                do_sample=False
            )[0]['summary_text']

            wrapped = textwrap.wrap(summary, width=110)
            return "\n\n".join([" ".join(wrapped[i:i+8]) for i in range(0, len(wrapped), 8)])
        except:
            return self._fallback_summary(text)

    def _generate_story_with_paragraphs(self, prompt, word_count):
        try:
            # Create a more structured prompt for the model
            structured_prompt = f"""Write a complete short story titled "{prompt}" with the following requirements:
            - Word count: approximately {word_count} words
            - Include a clear beginning, middle, and end
            - Develop at least one main character
            - Have a central conflict or challenge
            - Provide a resolution
            
            Story:\n"""
            
            story = self.story_gen(
                structured_prompt,
                max_length=min(1024, word_count*2),
                num_return_sequences=1,
                temperature=0.9,  # Slightly higher temperature for creativity
                top_k=50,
                top_p=0.95,
                repetition_penalty=1.2,  # Prevent repetition
                do_sample=True,
                truncation=True
            )[0]['generated_text']
            
            # Clean up the output
            story = story.replace(structured_prompt, "").strip()
            
            # Split into paragraphs and ensure proper formatting
            paragraphs = []
            current_para = []
            
            for line in story.split('\n'):
                line = line.strip()
                if line:
                    current_para.append(line)
                elif current_para:
                    paragraphs.append(" ".join(current_para))
                    current_para = []
            
            if current_para:
                paragraphs.append(" ".join(current_para))
                
            # Ensure we have a complete story
            if len(paragraphs) < 3:  # If output is too short
                return self._fallback_story(prompt)
                
            return "\n\n".join(paragraphs[:8])  # Return up to 8 paragraphs
            
        except Exception as e:
            print(f"Story generation error: {str(e)}")
            return self._fallback_story(prompt)

    def _fallback_summary(self, topic):
        return f"{topic} is a relevant topic with many important dimensions. It has societal, economic, and historical significance."

    def _fallback_story(self, prompt):
        return f"""The Jungle Monarch

Deep in the heart of the Amazon, a massive jaguar named Tikal ruled his territory with quiet authority. His golden eyes missed nothing as he patrolled his domain, the dappled sunlight through the canopy creating shifting patterns on his spotted coat.

One morning, Tikal discovered strange scents at the northern border of his kingdom. Humans had entered the jungle, bringing with them the sharp odor of metal and smoke. The other animals grew restless, their normal routines disrupted by this intrusion.

As days passed, the human presence grew stronger. Trees fell with thunderous crashes, and the jungle echoed with unfamiliar sounds. Tikal watched as monkeys fled their homes and birds abandoned their nests. The delicate balance of his world was being upended.

Determined to protect his kingdom, Tikal began a campaign of subtle intimidation. He left clear paw prints near the human camps. His deep, guttural roars echoed through the night, keeping the invaders uneasy. When a worker wandered too far alone, Tikal revealed himself just long enough to send the man running back to camp.

The humans, superstitious about the "ghost jaguar," began attributing their misfortunes to a jungle spirit. Equipment malfunctioned, supplies went missing, and an unshakable sense of being watched permeated their camp. Within a month, they packed up and left.

As the jungle reclaimed the abandoned clearing, Tikal returned to his favorite sunning rock. The monkeys chattered overhead, the birds returned to their nests, and the rhythm of the jungle resumed. The true king had defended his realm.

Word of the protected valley spread through the animal kingdom, and Tikal's legend grew. The jungle had its monarch, and he would tolerate no challengers to his throne."""

    def _fetch_web_content(self, query):
        try:
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            data = response.json()

            if not data.get('query', {}).get('search'):
                return None

            page_title = data['query']['search'][0]['title']
            page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(page_title.replace(' ', '_'))}"
            page_response = requests.get(page_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(page_response.text, 'html.parser')

            content = ""
            for paragraph in soup.select('#mw-content-text p'):
                text = paragraph.get_text().strip()
                if text and len(text) > 50:
                    content += text + "\n\n"
                    if len(content) > 5000:
                        break

            return content if content else None
        except:
            return None

    def _fetch_image(self, query, style=""):
        try:
            url = f"https://source.unsplash.com/600x400/?{urllib.parse.quote(query)},{style}"
            response = requests.get(url, headers=self.headers, stream=True, timeout=10)

            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                if not os.path.exists('temp'):
                    os.makedirs('temp')
                img_path = f"temp/{query[:15].replace(' ', '_')}_{random.randint(1,9999)}.jpg"
                img.save(img_path)
                return img_path
        except:
            return None
        return None

    def _save_pdf(self, content):
        filename = f"output/{content.get('title', content.get('topic', 'output'))[:20].replace(' ', '_')}.pdf"
        os.makedirs("output", exist_ok=True)

        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 16)

        if content['type'] == 'story':
            c.drawString(50, y, f"Story: {content['title']}")
        else:
            c.drawString(50, y, f"Summary: {content['topic']}")
        y -= 40

        if content['image']:
            try:
                img = ImageReader(content['image'])
                c.drawImage(img, 50, y - 200, width=500, height=200, preserveAspectRatio=True)
                y -= 220
            except:
                y -= 20

        c.setFont("Helvetica", 12)

        wrapped_text = textwrap.wrap(content['content'], width=100)
        for line in wrapped_text:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 12)
            c.drawString(50, y, line)
            y -= 18

        c.save()
        print(f"\n📄 PDF saved at: {filename}")