def condense_question(question:str,history:list,model)->str:
    if not history: return question
    lines=[]
    for item in history[-6:]:
        if isinstance(item,dict):
            lines.append(f"customer: {item.get('question','')}")
            lines.append(f"assistant: {item.get('answer','')}")
        else:
            lines.append(f"{getattr(item,'type','message')}: {getattr(item,'content',str(item))}")
    history_text='\n'.join(lines)
    prompt=('Rewrite the latest customer question as a standalone Pearlz support question using only relevant recent context. '
            'If it is a topic switch, do not carry over the old topic. Return only the rewritten question.\n'
            f'History:\n{history_text}\nLatest: {question}')
    return model.invoke(prompt).content.strip()
def append_history(history:list,question:str,answer:str,max_messages:int=12):
    history.extend([{'question':question,'answer':answer}])
    return history[-max_messages:]
