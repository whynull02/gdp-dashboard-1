import requests
import json

# API 서버 설정
API_URL = "http://localhost:8000"  # 실제 서버 IP로 변경하세요

# 1. GET 요청 - 전체 게시물 조회
def get_all_posts():
    response = requests.get(f"{API_URL}/api/posts")
    return response.json()

# 2. POST 요청 - 새 게시물 작성
def create_post(title, content):
    data = {
        "title": title,
        "content": content
    }
    response = requests.post(
        f"{API_URL}/api/posts",
        json=data
    )
    return response.json()

# 3. PUT 요청 - 게시물 수정
def update_post(post_id, title, content):
    data = {
        "title": title,
        "content": content
    }
    response = requests.put(
        f"{API_URL}/api/posts/{post_id}",
        json=data
    )
    return response.json()

# 4. DELETE 요청 - 게시물 삭제
def delete_post(post_id):
    response = requests.delete(f"{API_URL}/api/posts/{post_id}")
    return response.json()

if __name__ == "__main__":
    # 테스트 실행
    try:
        # 전체 게시물 조회
        print("\n1. 전체 게시물 조회:")
        posts = get_all_posts()
        print(json.dumps(posts, indent=2, ensure_ascii=False))

        # 새 게시물 작성
        print("\n2. 새 게시물 작성:")
        new_post = create_post("테스트 제목", "테스트 내용")
        print(json.dumps(new_post, indent=2, ensure_ascii=False))

        # 게시물 수정
        print("\n3. 게시물 수정:")
        updated_post = update_post(new_post['id'], "수정된 제목", "수정된 내용")
        print(json.dumps(updated_post, indent=2, ensure_ascii=False))

        # 게시물 삭제
        print("\n4. 게시물 삭제:")
        result = delete_post(new_post['id'])
        print(json.dumps(result, indent=2, ensure_ascii=False))

    except requests.exceptions.ConnectionError:
        print("API 서버에 연결할 수 없습니다.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
