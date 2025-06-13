# Slovack-board

A simple Flask app to manage posts with media, likes, and comments.

---

## Features

- Create posts with multiple media files (images/videos).  
- Like and unlike posts.  
- Comment on posts.  
- Admin panel to add, edit, and delete posts.  
- Image resizing to 1280x720 with black background padding.  
- Search posts by title or content.

---

## Requirements

- Python 3.7+  
- Flask  
- Pillow  
- pytz

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Dansvn/slovack-board.git
cd slovack-board
```

### 2. Create a virtual environment and install dependencies
```
python -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```
### 3. Run the app
```bash
python app.py
```
The app will run on http://localhost:5000

## Usage

- Access the admin panel at `/login` to create and manage posts.  
- Posts can include multiple images or videos.  
- Users can like/unlike and comment on posts on the public interface.  
- Search posts by keywords on the homepage.

---

## Notes

- Media files are saved in `static/uploads`.  
- Admin credentials are stored in the code (`ADMINS` dict). Change before production.  
- Timezone is set to São Paulo (BRT) for post timestamps.  

![print1](https://github.com/user-attachments/assets/83f8c237-87ad-4a57-a929-e1a4a714fe7e)
![print2](https://github.com/user-attachments/assets/4ea5f4cb-b7e8-4541-b955-547f5ef51490)
![print3](https://github.com/user-attachments/assets/b5251a0b-7a30-4887-960f-8fa51f67031b)
![print4](https://github.com/user-attachments/assets/32a23f72-6c34-42da-8071-b976967430d0)



---

## Contact


If you have any questions or need support, feel free to reach out!  
**My social links:** [ayo.so/dansvn](https://ayo.so/dansvn)



