1- create dockerfile and build the image

2- run the image in the background

3- expose the port 8003 to 8000

4- run below commands


'''
get all tasks --> curl http://localhost:8003/tasks

get specific task --> curl http://localhost:8003/tasks/1


add new task -->

curl -X POST http://localhost:8003/tasks \
-H "Content-Type: application/json" \
-d '{"title":"Learn Docker Volumes"}'


delete specific task --> curl -X DELETE http://localhost:8003/tasks/1

'''
