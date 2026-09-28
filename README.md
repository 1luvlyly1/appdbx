
    Tạo một thư mục trong Workspace, ví dụ /Workspace/Users/<bạn>/sv-test-app, rồi upload 3 file vào đó.
    Vào Compute → Apps → Create app → Custom app và đặt tên app.
    Ở phần App resources, bấm Add resource → Serving endpoint, chọn endpoint Sonnet (hoặc Haiku), quyền Can query, và đặt resource key đúng là serving-endpoint. File app.yaml đọc tên endpoint qua key này. Nếu đặt key khác, app sẽ dùng mặc định databricks-claude-sonnet-4-5.
    Deploy từ thư mục ở bước 1, rồi mở link của app.
