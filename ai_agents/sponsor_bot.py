import os
import smtplib
import json
import time
import requests
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SponsorBot:
    def __init__(self):
        self.bot_email = os.getenv('BOT_EMAIL')
        self.bot_password = os.getenv('BOT_PASSWORD')
        self.hf_token = os.getenv('HF_TOKEN')
        self.api_url = os.getenv('PRODUCTION_URL', 'https://arena-x.onrender.com')
        self.sponsor_db = "sponsors.json"
        self.templates = {
            'initial': "templates/initial_template.txt",
            'followup': "templates/followup_template.txt",
            'tournament': "templates/tournament_template.txt"
        }
        self.sponsors = self.load_sponsors()
        
    def load_sponsors(self):
        """Load sponsor database"""
        try:
            with open(self.sponsor_db, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_sponsors(self):
        """Save sponsor database"""
        with open(self.sponsor_db, 'w') as f:
            json.dump(self.sponsors, f, indent=2)
    
    def find_new_sponsors(self):
        """Find potential sponsors using AI"""
        prompt = """
        Generate a list of 10 potential sponsors for ArenaX, an esports gaming platform.
        Include company name, contact email, and industry.
        Return in JSON format: [{"name": "", "email": "", "industry": ""}]
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/EleutherAI/gpt-neox-20b",
                headers=headers,
                json=payload
            )
            
            # Extract JSON from response
            result = response.json()[0]['generated_text']
            start = result.find('[')
            end = result.rfind(']') + 1
            new_sponsors = json.loads(result[start:end])
            
            # Add to database if not exists
            for sponsor in new_sponsors:
                if not any(s['email'] == sponsor['email'] for s in self.sponsors):
                    sponsor.update({
                        "last_contact": None,
                        "status": "new",
                        "responses": []
                    })
                    self.sponsors.append(sponsor)
            
            self.save_sponsors()
            return True
        except Exception as e:
            print(f"Sponsor discovery failed: {str(e)}")
            return False
    
    def personalize_email(self, sponsor, template_type):
        """Personalize email using AI"""
        # Get template
        try:
            with open(self.templates[template_type], 'r') as f:
                template = f.read()
        except FileNotFoundError:
            template = ""
        
        prompt = f"""
        Personalize this sponsorship email for {sponsor['name']} in {sponsor['industry']}:
        
        Template:
        {template}
        
        Include specific reasons why ArenaX would be valuable for their industry.
        Keep it under 200 words.
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/EleutherAI/gpt-neox-20b",
                headers=headers,
                json=payload
            )
            return response.json()[0]['generated_text']
        except Exception:
            return template
    
    def send_email(self, to_email, subject, body):
        """Send email to sponsor"""
        msg = MIMEMultipart()
        msg['From'] = self.bot_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.bot_email, self.bot_password)
            server.sendmail(self.bot_email, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Email failed: {str(e)}")
            return False
    
    def get_tournament_data(self):
        """Get upcoming tournament data from API"""
        try:
            response = requests.get(f"{self.api_url}/tournaments/upcoming")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def run_campaign(self, campaign_type='initial'):
        """Run sponsorship campaign"""
        # Refresh sponsor list weekly
        if datetime.now().weekday() == 0:  # Monday
            self.find_new_sponsors()
        
        # Get upcoming tournaments
        tournaments = self.get_tournament_data() or []
        featured_tournament = tournaments[0] if tournaments else None
        
        # Process sponsors
        for sponsor in self.sponsors:
            # Skip recently contacted
            if sponsor.get('last_contact') and \
               (datetime.now() - datetime.fromisoformat(sponsor['last_contact'])).days < 7:
                continue
                
            # Determine email type
            if sponsor['status'] == 'new':
                email_type = 'initial'
            elif sponsor['status'] == 'contacted' and featured_tournament:
                email_type = 'tournament'
            else:
                email_type = 'followup'
            
            # Personalize email
            subject = f"Sponsorship Opportunity with ArenaX Esports"
            if email_type == 'tournament':
                subject = f"Feature Your Brand in our {featured_tournament['name']} Tournament"
            
            body = self.personalize_email(sponsor, email_type)
            
            # Add tournament details
            if featured_tournament and email_type == 'tournament':
                body += f"\n\nTournament Details:\n"
                body += f"Name: {featured_tournament['name']}\n"
                body += f"Date: {featured_tournament['date']}\n"
                body += f"Expected Participants: {featured_tournament['participants']}\n"
                body += f"Prize Pool: ${featured_tournament['prize_pool']}\n"
                body += f"Sponsorship Package: ${featured_tournament['sponsorship_fee']}"
            
            # Send email
            if self.send_email(sponsor['email'], subject, body):
                # Update sponsor record
                sponsor['last_contact'] = datetime.now().isoformat()
                sponsor['status'] = 'contacted'
                sponsor['campaign'] = campaign_type
                self.save_sponsors()
                
                # Space out emails
                time.sleep(random.randint(60, 300))  # 1-5 minutes
    
    def handle_response(self, email_text):
        """Handle email responses using AI"""
        prompt = f"""
        Analyze this sponsor email response and determine next steps:
        {email_text}
        
        Classify as:
        - 'positive': Shows interest, asks questions
        - 'negative': Declines clearly
        - 'neutral': Needs follow-up
        
        If positive, suggest talking points for next email.
        Return in JSON format: {{"sentiment": "", "next_steps": "", "talking_points": ""}}
        """
        
        try:
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 300,
                    "temperature": 0.5
                }
            }
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/EleutherAI/gpt-neox-20b",
                headers=headers,
                json=payload
            )
            
            # Extract JSON from response
            result = response.json()[0]['generated_text']
            start = result.find('{')
            end = result.rfind('}') + 1
            return json.loads(result[start:end])
        except Exception:
            return {"sentiment": "unknown", "next_steps": "Follow up in 7 days", "talking_points": ""}
    
    def process_inbox(self):
        """Process email responses (simplified version)"""
        # In production, this would connect to an IMAP server
        # For demo, we'll simulate processing
        for sponsor in self.sponsors:
            if sponsor['status'] == 'contacted' and random.random() < 0.2:  # 20% chance of response
                response_types = [
                    "We're interested! Send more details.",
                    "Not interested at this time.",
                    "What are your sponsorship tiers?"
                ]
                response = random.choice(response_types)
                analysis = self.handle_response(response)
                
                # Update sponsor record
                sponsor['responses'].append({
                    "date": datetime.now().isoformat(),
                    "response": response,
                    "analysis": analysis
                })
                
                if analysis['sentiment'] == 'positive':
                    sponsor['status'] = 'hot-lead'
                elif analysis['sentiment'] == 'negative':
                    sponsor['status'] = 'closed'
                
                self.save_sponsors()

if __name__ == "__main__":
    bot = SponsorBot()
    
    # Run campaigns on different schedules
    while True:
        now = datetime.now()
        
        # Daily at 10AM
        if now.hour == 10:
            bot.process_inbox()
            
            # Mondays: Initial outreach
            if now.weekday() == 0:
                bot.run_campaign('initial')
            
            # Wednesdays: Tournament-specific
            elif now.weekday() == 2:
                bot.run_campaign('tournament')
            
            # Fridays: Follow-ups
            elif now.weekday() == 4:
                bot.run_campaign('followup')
        
        time.sleep(3600)  # Check hourly
