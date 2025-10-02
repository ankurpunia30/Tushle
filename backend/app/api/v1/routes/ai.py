from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import httpx
import json

from app.db.database import get_db
from app.models import AIScript, User
from app.core.security import get_current_active_user
from app.core.config import settings

router = APIRouter()


class ScriptGenerateRequest(BaseModel):
    topic: str
    video_style: str = "educational"
    target_duration: int = 60  # seconds
    tone: str = "professional"
    include_hook: bool = True


class ScriptResponse(BaseModel):
    id: int
    topic: str
    script_content: str
    video_style: str
    target_duration: int
    status: str
    
    class Config:
        from_attributes = True


@router.post("/generate-script", response_model=ScriptResponse)
async def generate_script(
    request: ScriptGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate AI script using Ollama"""
    
    # Create prompt for script generation
    prompt = f"""
    Create a {request.video_style} script about: {request.topic}
    
    Requirements:
    - Target duration: {request.target_duration} seconds
    - Tone: {request.tone}
    - {'Include a compelling hook in the first 5 seconds' if request.include_hook else ''}
    
    Format the script with clear sections:
    [HOOK] (if requested)
    [INTRODUCTION]
    [MAIN CONTENT]
    [CONCLUSION]
    [CALL TO ACTION]
    
    Make it engaging and actionable.
    """
    
    try:
        # Call Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": "llama2",  # or any available model
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                script_content = result.get("response", "")
            else:
                # Fallback content if Ollama is not available
                script_content = f"""[HOOK]
Did you know that {request.topic} could change everything?

[INTRODUCTION]
Today we're diving deep into {request.topic}, and by the end of this video, you'll have a complete understanding of how to leverage this effectively.

[MAIN CONTENT]
Let me break this down into three key points:

1. The fundamental concepts behind {request.topic}
2. Practical applications you can implement today
3. Advanced strategies for maximum impact

[CONCLUSION]
Understanding {request.topic} is crucial for staying ahead in today's landscape.

[CALL TO ACTION]
If you found this valuable, subscribe for more insights and let me know in the comments what topic you'd like me to cover next!"""
                
    except Exception as e:
        # Fallback content
        script_content = f"""[HOOK]
Let's explore {request.topic} together!

[INTRODUCTION]
In this video, we'll cover everything you need to know about {request.topic}.

[MAIN CONTENT]
Here are the key insights about {request.topic}:
- Core concepts and principles
- Practical implementation strategies
- Best practices and common pitfalls to avoid

[CONCLUSION]
{request.topic} offers incredible opportunities when approached correctly.

[CALL TO ACTION]
Subscribe for more content and share your thoughts in the comments!"""
    
    # Save to database
    ai_script = AIScript(
        topic=request.topic,
        script_content=script_content,
        video_style=request.video_style,
        target_duration=request.target_duration,
        status="generated",
        metadata={
            "tone": request.tone,
            "include_hook": request.include_hook,
            "generated_by": current_user.id
        }
    )
    
    db.add(ai_script)
    db.commit()
    db.refresh(ai_script)
    
    return ai_script


@router.get("/scripts", response_model=List[ScriptResponse])
async def get_scripts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all generated scripts"""
    scripts = db.query(AIScript).order_by(AIScript.created_at.desc()).all()
    return scripts


@router.get("/scripts/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific script by ID"""
    script = db.query(AIScript).filter(AIScript.id == script_id).first()
    
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found"
        )
    
    return script


@router.delete("/scripts/{script_id}")
async def delete_script(
    script_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a script"""
    script = db.query(AIScript).filter(AIScript.id == script_id).first()
    
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found"
        )
    
    db.delete(script)
    db.commit()
    
    return {"message": "Script deleted successfully"}
