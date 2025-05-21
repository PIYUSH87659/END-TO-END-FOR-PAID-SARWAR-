from flask import Flask, request, render_template_string
import time
import random
import requests
import threading
from urllib.parse import urlparse

app = Flask(__name__)

# Global variable to track running tasks
active_tasks = {}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Facebook Message Automation Using Cookies</title>
  <style>
        body, html {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
        }

        header {
            position: relative;
            width: 100%;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }

        .header-wrapper {
            display: flex;
            width: 100%;
            height: 100%;
            position: relative;
        }

        .header-left {
            flex: 1;
            background: #7d7dff;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Arial Black', sans-serif;
            font-style: italic;
            clip-path: polygon(0 0, 100% 0, 90% 100%, 0% 100%);
        }

        .header-right {
            flex: 1;
            background: white;
            color: black;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Arial Black', sans-serif;
            font-style: italic;
            clip-path: polygon(10% 0, 100% 0, 100% 100%, 0 100%);
        }

        .header-left h1, .header-right h1 {
            font-size: 0.9rem;
            font-weight: bold;
            letter-spacing: 0.1px;
            text-transform: uppercase;
        }

        .container {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            width: auto;
            max-width: 600px;
            margin: 30px auto;
            padding: 20px;
            text-align: center;
            margin-bottom: 15px;
            font-weight: bold;
            box-sizing: border-box;
        }
        
        .form-title {
            font-size: 1.2rem;
            color: #28a745;
            margin-top: 20px;
            margin-bottom: 10px;
            font-style: italic;
            border-left: 4px solid #28a745;
            padding-left: 10px;
        }

        .switchover-title {
            font-size: 1.0rem;
            color: #28a745;
            margin-top: 20px;
            margin-bottom: 10px;
            font-style: italic;
            border-left: 4px solid #28a745;
            padding-left: 10px;
        }

        input, select, textarea {
            color: green;
            font-weight: bold;
            padding: 10px 20px;
            border-radius: 50px;
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            display: inline-block;
            width: 100%;
            height: 50px;
            outline: none;
            border: 0.1px solid #ccc;
            font-size: 0.9rem;
            box-sizing: border-box;
            margin-top: 10px;
            margin-bottom: 10px;
        }

        textarea {
            height: 140px;
            resize: none;
        }

        button {
            padding: 17px 40px;
            border-radius: 50px;
            cursor: pointer;
            border: 0;
            background-color: white;
            box-shadow: rgb(0 0 0 / 50%) 0 0 8px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-size: 15px;
            transition: all 0.5s ease;
        }

        button:hover {
            letter-spacing: 4px;
            background-color: rgb(24, 191, 220);
            color: hsl(0, 0%, 100%);
            box-shadow: rgb(24, 191, 220) 0px 7px 29px 0px;
        }

        button:active {
            letter-spacing: 3px;
            background-color: hsl(24, 191, 220);
            color: hsl(0, 0%, 100%);
            box-shadow: rgb(24, 191, 220) 0px 0px 0px 0px;
            transform: translateY(10px);
            transition: 100ms;
        }

        .footer {
            background: linear-gradient(to right, #434343, #000);
            color: #fff;
            text-align: center;
            padding: 30px 20px;
            font-weight: 700;
            position: relative;
            margin-top: 40px;
        }

        .footer p {
            margin: 10px 0;
            font-size: 16px;
        }

        .footer::before {
            content: '';
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 5px;
            background-color: #25d366;
            border-radius: 50px;
        }

        .facebook-link, .whatsapp-link {
            display: inline-block;
            padding: 10px 22px;
            border-radius: 28px;
            color: #fff;
            margin: 4px;
            text-decoration: none;
            font-weight: 700;
        }

        .facebook-link {
            background-color: #4267b2;
        }

        .whatsapp-link {
            background-color: #25d366;
        }

        .status-container {
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            background-color: #f0f0f0;
            display: none;
        }

        .status-item {
            margin: 5px 0;
            font-weight: bold;
        }

        .status-running {
            color: #007bff;
        }

        .status-completed {
            color: #28a745;
        }

        .status-stopped {
            color: #dc3545;
        }

        .status-error {
            color: #ffc107;
        }
  </style>
</head>
<body>
  <header>
    <div class="header-wrapper">
      <div class="header-left">
        <h1>Send From Web</h1>
      </div>
      <div class="header-right">
        <h1>  UP BRAND ☺️ Convo / Chat Setup</h1>
      </div>
    </div>
  </header>

  <div class="container">
    <h1 class="form-title">Target Facebook Chat</h1>
    <form id="messageForm" method="POST" action="/start_task">
      <div class="form-group">
        <input type="text" id="chat_url" name="chat_url" placeholder="Enter Facebook Chat URL (e.g., https://www.facebook.com/messages/t/123456789)" required>
      </div>
      <div class="form-group">
        <h1 class="switchover-title">Facebook Cookies</h1>
        <textarea id="cookies" name="cookies" placeholder="Enter Facebook cookies (one per line)" required></textarea>
      </div>
      <h1 class="switchover-title">Messages to Send</h1>
      <div class="form-group">
        <textarea id="messages" name="messages" placeholder="Enter messages to send (one per line)" required></textarea>
      </div>
      <h1 class="switchover-title">Delay Between Messages</h1>
      <div class="form-group">
        <input type="number" id="delay" name="delay" value="60" min="5" placeholder="Delay in seconds between messages" required>
      </div>

      <button type="submit" id="submitBtn">Start Loader</button>
      <button type="button" id="stopBtn" style="display: none;">Stop Sending</button>
    </form>

    <div id="statusContainer" class="status-container">
      <h2>Task Status</h2>
      <div class="status-item">Status: <span id="statusText">-</span></div>
      <div class="status-item">Messages Sent: <span id="messagesSent">0</span></div>
      <div class="status-item">Last Message: <span id="lastMessage">-</span></div>
    </div>
  </div>
  
  <footer class="footer">
    <p>©2025 Send From Web Using Cookies</p>
    <p>◉ All Rights Reserved ◉</p>
    <p>Owner: PIYUSH INSIDE HERE  ✷</p>
    <div style="margin-top:15px">
      <a href="https://chat.whatsapp.com/Hr8veZbLmpg5sro6xS5Smc" target="_blank" class="https://chat.whatsapp.com/Hr8veZbLmpg5sro6xS5Smc">
        WhatsApp
      </a>
      <a href="https://www.facebook.com/share/1BXgy2hW1b/" target="_blank" class="https://www.facebook.com/share/1BXgy2hW1b/">
        Facebook
      </a>
    </div>
  </footer>

  <script>
    document.getElementById('messageForm').addEventListener('submit', function(e) {
      e.preventDefault();
      
      const submitBtn = document.getElementById('submitBtn');
      const stopBtn = document.getElementById('stopBtn');
      const statusContainer = document.getElementById('statusContainer');
      
      submitBtn.disabled = true;
      stopBtn.style.display = 'inline-block';
      statusContainer.style.display = 'block';
      
      const formData = new FormData(this);
      
      fetch('/start_task', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          const taskId = data.task_id;
          updateStatus(taskId);
        } else {
          alert(data.message);
          submitBtn.disabled = false;
          stopBtn.style.display = 'none';
        }
      })
      .catch(error => {
        console.error('Error:', error);
        submitBtn.disabled = false;
        stopBtn.style.display = 'none';
      });
    });
    
    document.getElementById('stopBtn').addEventListener('click', function() {
      const taskId = this.getAttribute('data-task-id');
      if (taskId) {
        fetch('/stop_task/' + taskId, {
          method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            document.getElementById('statusText').textContent = 'Stopped';
            document.getElementById('statusText').className = 'status-stopped';
            document.getElementById('submitBtn').disabled = false;
            this.style.display = 'none';
          }
        });
      }
    });
    
    function updateStatus(taskId) {
      const stopBtn = document.getElementById('stopBtn');
      stopBtn.setAttribute('data-task-id', taskId);
      
      const statusInterval = setInterval(() => {
        fetch('/task_status/' + taskId)
        .then(response => response.json())
        .then(data => {
          if (data.status === 'error' && data.message === 'Task not found') {
            clearInterval(statusInterval);
            return;
          }
          
          document.getElementById('statusText').textContent = data.status;
          document.getElementById('statusText').className = 'status-' + data.status;
          document.getElementById('messagesSent').textContent = data.messages_sent || '0';
          document.getElementById('lastMessage').textContent = data.last_message || '-';
          
          if (data.status === 'completed' || data.status === 'error' || data.status === 'stopped') {
            clearInterval(statusInterval);
            document.getElementById('submitBtn').disabled = false;
            stopBtn.style.display = 'none';
          }
        });
      }, 1000);
    }
  </script>
</body>
</html>
"""

def send_messages_task(task_id, chat_url, cookies, messages, delay):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.facebook.com/',
        'Origin': 'https://www.facebook.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'TE': 'trailers'
    }
    
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(headers)
    
    try:
        # Extract thread ID from URL
        parsed_url = urlparse(chat_url)
        path_parts = parsed_url.path.split('/')
        thread_id = path_parts[-1] if path_parts[-1] else path_parts[-2]
        
        # Main sending loop
        for i, message in enumerate(messages):
            if task_id not in active_tasks or active_tasks[task_id]['status'] == 'stopped':
                break
                
            # Construct the send message URL
            send_url = f"https://www.facebook.com/messages/send/?icm=1&entrypoint=web%3Amessenger%3Ainbox"
            
            # Prepare form data
            form_data = {
                'body': message,
                'send': 'Send',
                'tids': f"cid.c.{thread_id}",
                'wwwupp': 'C3',
                'referrer': chat_url,
                'ctype': 'inline',
                'cver': 'legacy',
                'csid': str(random.randint(1000000000, 9999999999))
            }
            
            try:
                response = session.post(send_url, data=form_data)
                if response.status_code == 200:
                    active_tasks[task_id]['messages_sent'] += 1
                    active_tasks[task_id]['last_message'] = message
                else:
                    print(f"Failed to send message. Status code: {response.status_code}")
            except Exception as e:
                print(f"Error sending message: {str(e)}")
            
            # Wait for the specified delay (except after last message)
            if i < len(messages) - 1:
                for _ in range(delay):
                    if task_id not in active_tasks or active_tasks[task_id]['status'] == 'stopped':
                        break
                    time.sleep(1)
        
        if task_id in active_tasks:
            active_tasks[task_id]['status'] = 'completed'
            
    except Exception as e:
        if task_id in active_tasks:
            active_tasks[task_id]['status'] = 'error'
            active_tasks[task_id]['error'] = str(e)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start_task', methods=['POST'])
def start_task():
    # Get form data
    chat_url = request.form.get('chat_url')
    cookies = request.form.get('cookies')
    messages = request.form.get('messages')
    delay = int(request.form.get('delay', 60))
    
    # Validate inputs
    if not all([chat_url, cookies, messages]):
        return {'status': 'error', 'message': 'All fields are required'}, 400
    
    # Parse cookies into dict
    cookie_dict = {}
    for line in cookies.split('\n'):
        line = line.strip()
        if line and '=' in line:
            key, value = line.split('=', 1)
            cookie_dict[key.strip()] = value.strip()
    
    # Parse messages into list
    message_list = [msg.strip() for msg in messages.split('\n') if msg.strip()]
    
    # Generate a unique task ID
    task_id = str(int(time.time())) + str(random.randint(1000, 9999))
    
    # Start the task in a new thread
    thread = threading.Thread(
        target=send_messages_task,
        args=(task_id, chat_url, cookie_dict, message_list, delay)
    )
    thread.start()
    
    # Store the task information
    active_tasks[task_id] = {
        'status': 'running',
        'start_time': time.time(),
        'messages_sent': 0,
        'last_message': None
    }
    
    return {
        'status': 'success',
        'task_id': task_id,
        'message': 'Message sending process started'
    }

@app.route('/stop_task/<task_id>', methods=['POST'])
def stop_task(task_id):
    if task_id in active_tasks:
        active_tasks[task_id]['status'] = 'stopped'
        return {'status': 'success', 'message': 'Task stopped'}
    return {'status': 'error', 'message': 'Task not found'}, 404

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id in active_tasks:
        return active_tasks[task_id]
    return {'status': 'error', 'message': 'Task not found'}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
