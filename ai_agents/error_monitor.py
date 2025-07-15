import os
import requests
import json
import time
import subprocess
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ErrorMonitor:
    def __init__(self):
        self.api_url = os.getenv('PRODUCTION_URL', 'https://arena-x.onrender.com')
        self.github_repo = os.getenv('GITHUB_REPO')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.admin_email = os.getenv('ADMIN_EMAIL')
        self.bot_email = os.getenv('BOT_EMAIL')
        self.bot_password = os.getenv('BOT_PASSWORD')
        self.hf_token = os.getenv('HF_TOKEN')
        self.error_threshold = 10  # Errors per minute threshold
        self.health_check_interval = 300  # 5 minutes
        self.error_logs = []
        
    def health_check(self):
        """Check server health status"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def analyze_logs(self):
        """Analyze error logs using AI"""
        if not self.error_logs:
            return None
            
        log_sample = "\n".join(self.error_logs[-5:])  # Last 5 errors
        prompt = f"""
        Analyze these application errors and suggest fixes:
        {log_sample}
        
        Recommendations should include:
        1. Root cause analysis
        2. Code changes needed
        3. Configuration adjustments
        4. Severity level (1-5)
        """
        
        return self.query_ai(prompt)
    
    def query_ai(self, prompt):
        """Query Hugging Face AI model"""
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(
                "https://api-inference.huggingface.co/models/EleutherAI/gpt-neox-20b",
                headers=headers,
                json=payload
            )
            return response.json()[0]['generated_text']
        except Exception as e:
            return f"AI query failed: {str(e)}"
    
    def auto_fix_code(self, file_path, error_context):
        """Automatically fix code using AI"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            prompt = f"""
            Fix this code based on error analysis:
            {error_context}
            
            Original code:
            {code}
            
            Return only the fixed code with no explanations.
            """
            
            fixed_code = self.query_ai(prompt)
            
            # Create backup
            backup_path = f"{file_path}.bak.{int(time.time())}"
            with open(backup_path, 'w') as f:
                f.write(code)
            
            # Write fixed code
            with open(file_path, 'w') as f:
                f.write(fixed_code)
                
            return True, fixed_code
        except Exception as e:
            return False, str(e)
    
    def rollback_code(self):
        """Rollback to last working commit"""
        try:
            subprocess.run(['git', 'reset', '--hard', 'HEAD^'], check=True)
            subprocess.run(['git', 'push', '--force'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            return False
    
    def restart_service(self):
        """Restart the server service"""
        try:
            # For Render.com service restart
            service_id = os.getenv('RENDER_SERVICE_ID')
            api_key = os.getenv('RENDER_API_KEY')
            
            if service_id and api_key:
                response = requests.post(
                    f"https://api.render.com/v1/services/{service_id}/restart",
                    headers={'Authorization': f'Bearer {api_key}'}
                )
                return response.status_code == 200
            return False
        except Exception:
            return False
    
    def create_github_issue(self, title, body):
        """Create a GitHub issue for critical errors"""
        if not self.github_repo or not self.github_token:
            return False
            
        url = f"https://api.github.com/repos/{self.github_repo}/issues"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "title": title,
            "body": body,
            "labels": ["bug", "auto-generated"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            return response.status_code == 201
        except Exception:
            return False
    
    def send_alert_email(self, subject, body):
        """Send alert email to admin"""
        if not self.admin_email or not self.bot_email:
            return False
            
        msg = MIMEMultipart()
        msg['From'] = self.bot_email
        msg['To'] = self.admin_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.bot_email, self.bot_password)
            server.sendmail(self.bot_email, self.admin_email, msg.as_string())
            server.quit()
            return True
        except Exception:
            return False
    
    def monitor(self):
        """Main monitoring loop"""
        error_count = 0
        last_alert_time = 0
        
        while True:
            # Health check
            if not self.health_check():
                error_count += 1
                self.error_logs.append(f"{datetime.now()} - Health check failed")
                
                # Analyze after 3 consecutive failures
                if error_count >= 3:
                    analysis = self.analyze_logs() or "No analysis available"
                    
                    # Try automatic fixes for known patterns
                    if "database connection" in analysis.lower():
                        self.restart_service()
                    elif "code error" in analysis.lower():
                        # Try to fix server/main.py
                        success, _ = self.auto_fix_code("server/main.py", analysis)
                        if success:
                            self.restart_service()
                    
                    # Rollback if still failing after fixes
                    time.sleep(60)
                    if not self.health_check():
                        self.rollback_code()
                        self.restart_service()
                        
                    # Create GitHub issue
                    issue_title = "Critical Service Failure"
                    self.create_github_issue(issue_title, analysis)
                    
                    # Send email alert if not sent recently
                    if time.time() - last_alert_time > 3600:  # 1 hour cooldown
                        email_body = f"""
                        Critical service failure detected!
                        
                        Analysis:
                        {analysis}
                        
                        Actions taken:
                        - Automatic fixes attempted
                        - Rollback to previous version
                        - Service restarted
                        
                        GitHub issue created for tracking.
                        """
                        self.send_alert_email("CRITICAL: Service Down", email_body)
                        last_alert_time = time.time()
            
            # Reset error count if healthy
            else:
                error_count = 0
            
            # Check for high error rate
            recent_errors = [e for e in self.error_logs if 
                            datetime.now() - datetime.strptime(e.split(' - ')[0], '%Y-%m-%d %H:%M:%S.%f') < timedelta(minutes=1)]
            
            if len(recent_errors) > self.error_threshold:
                analysis = self.analyze_logs() or "No analysis available"
                issue_title = "High Error Rate Detected"
                self.create_github_issue(issue_title, analysis)
            
            time.sleep(self.health_check_interval)

if __name__ == "__main__":
    monitor = ErrorMonitor()
    monitor.monitor()
