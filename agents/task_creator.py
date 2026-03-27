@app.post("/agents/task-creator")
async def ai_task_creator(data: AICommand):
    try:
        # 1. Update the PM Boss prompt for multiple tasks
        prompt = ChatPromptTemplate.from_template("""
        You are the 'AI PM Boss'. Your job is to take a raw requirement and 
        break it down into 3-5 professional, actionable engineering tasks.
        
        Requirement: {user_input}
        
        Return ONLY a JSON list of strings. 
        Example Output: ["Setup database schema", "Create API endpoints", "Build frontend UI"]
        """)

        # 2. Setup the Chain with a JSON Parser
        chain = prompt | llm | JsonOutputParser()
        
        # 3. Run the AI Agent
        task_list = chain.invoke({"user_input": data.command})
        
        # 4. Insert each task into PostgreSQL (Layer 3: Automated Outputs)
        for task_title in task_list:
            query = """
                INSERT INTO tasks (title, status, project_id) 
                VALUES (:title, :status, :project_id)
            """
            await database.execute(query=query, values={
                "title": f"🤖 {task_title}",
                "status": "todo",
                "project_id": data.project_id
            })
        
        return {"message": f"AI Agent successfully decomposed requirements into {len(task_list)} tasks."}
        
    except Exception as e:
        print(f"AI Error: {e}")
        return {"error": "The AI Agent failed to decompose the task. Check API limits."}