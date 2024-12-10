from psl_proof.models.cargo_data import CargoData, ChatData, SourceChatData, SourceData
from psl_proof.models.proof_response import ProofResponse
from typing import List, Dict, Any
from psl_proof.utils.feature_extraction import get_sentiment_data, get_keywords_keybert #, get_keywords_lda
from psl_proof.utils.submit_data import validate_proof_data

def score_uniqueness(source_data : SourceChatData) -> float:
    result = validate_proof_data(
        source_data
    )
    if result is None:
        return 0
    return result.uniqueness


def validate_data(
    config: Dict[str, Any],
    cargo_data : CargoData,
    proof_data : ProofResponse
) :
    source_data : SourceChatData = cargo_data.source_data
    source_chats = source_data.source_chats

    score_threshold = 0.5
    number_of_keywords = 10

    total_quality = 0.00
    chat_count = 0

    #Validate source data via valiator.api & obtain unquiness
    proof_data.uniqueness = score_uniqueness(
        source_data
    )

    # Loop through the chat_data_list
    for source_chat in source_chats:

        #print(f"source_chat:{source_chat}")
        chat_count += 1  # Increment chat count
        source_contents = None
        contents_length = 0
        if source_chat.contents:  # Ensure chat_contents is not None
            source_contents = source_chat.content_as_text()
            print(f"source_contents: {source_contents}")
            contents_length = len(source_contents)

        if (contents_length > 0):

            chat_id = source_chat.chat_id

            quality = source_chat.quality_score()
            print(f"Chat({chat_id}) - quality: {quality}")
            total_quality += quality

            #print(f"source_contents: {source_contents}")
            # if chat data has meaningful data...
            if quality > score_threshold:
                # content is unique...
                chat_sentiment = get_sentiment_data(
                    source_contents
                )
                chat_keywords_keybert = get_keywords_keybert(
                    source_contents,
                    number_of_keywords
                )
                # Create a ChatData instance and add it to the list
                chat_data = ChatData(
                    chat_id=source_chat.chat_id,
                    chat_length=contents_length,
                    sentiment=chat_sentiment,
                    keywords=chat_keywords_keybert
                )
                #print(f"chat_data: {chat_data}")
                cargo_data.chat_list.append(
                    chat_data
                )

    # Calculate uniqueness if there are chats
    if chat_count > 0:
        proof_data.quality = round(total_quality / chat_count, 2)
        print(f"proof_data.quality: {proof_data.quality}")