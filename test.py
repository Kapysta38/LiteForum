from requests import get, post, delete

# Тестирование user API
'''print(get('http://localhost:5000/api/v1/users').json())
print(get('http://localhost:5000/api/v1/users/1').json())
print(get('http://localhost:5000/api/v1/users/100').json())
print(post('http://localhost:5000/api/v1/users').json())
print(post('http://localhost:5000/api/v1/users', json={'surname': 'gagav'}).json())
print(post('http://localhost:5000/api/v1/users', json={'name': 'Игорь',
                                                       'email': 'vinnipyx3@gmail.com',
                                                       'password': '321'}).json())
print(delete('http://localhost:5000/api/v1/users/5').json())
'''

# Тестирование chats API
'''print(get('http://localhost:5000/api/v1/chats').json())
print(get('http://localhost:5000/api/v1/chats/1').json())
print(get('http://localhost:5000/api/v1/chats/100').json())
print(post('http://localhost:5000/api/v1/chats').json())
print(post('http://localhost:5000/api/v1/chats', json={'surname': 'gagav'}).json())
print(post('http://localhost:5000/api/v1/chats', json={'title': 'Игорь',
                                                       'is_private': False,
                                                       'user_id': 1}).json())
print(delete('http://localhost:5000/api/v1/chats/1').json())'''

# Тестирование comment API
'''print(get('http://localhost:5000/api/v1/comment').json())
print(get('http://localhost:5000/api/v1/comment/10').json())
print(get('http://localhost:5000/api/v1/comment/100').json())
print(post('http://localhost:5000/api/v1/comment').json())
print(post('http://localhost:5000/api/v1/comment', json={'surname': 'gagav'}).json())
print(post('http://localhost:5000/api/v1/comment', json={'author': 'Новый форум 2',
                                                       'text': 'False',
                                                       'chat_id': 1}).json())
print(post('http://localhost:5000/api/v1/comment', json={'author': 'Винни Play',
                                                       'text': 'False',
                                                       'chat_id': 1}).json())
print(post('http://localhost:5000/api/v1/comment', json={'author': 'Винни Play',
                                                       'text': 'True',
                                                       'chat_id': 2}).json())
print(delete('http://localhost:5000/api/v1/comment/5').json())'''
