from typing import List

def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """
    Chunks a long text into smaller pieces, trying to split at paragraph or sentence boundaries.
    """
    chunks = []
    current_chunk = ""
    paragraphs = text.split("\n\n")  # Split by paragraphs

    for paragraph in paragraphs:
        sentences = paragraph.split(". ")  # Split by sentences within paragraphs
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= chunk_size: # +2 for ". " separator
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". " # Start a new chunk
        if current_chunk: # Process remaining sentences after paragraph split
            if len(current_chunk.split()) > chunk_size/4: # if the last paragraph is too big, chunk it by lines
                 lines = current_chunk.splitlines()
                 for line in lines:
                    if len(current_chunk) + len(line) + 1 <= chunk_size: # +1 for "\n" separator
                        current_chunk += line + "\n"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = line + "\n"
                 if current_chunk: # Append the last chunk
                    chunks.append(current_chunk.strip())

            else:
                chunks.append(current_chunk.strip()) # Append the chunk if small enough
            current_chunk = "" # Reset current chunk for next paragraph


    return chunks
