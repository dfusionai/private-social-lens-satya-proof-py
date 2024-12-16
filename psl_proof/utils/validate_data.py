from psl_proof.models.cargo_data import CargoData, ChatData, SourceChatData, SourceData
from psl_proof.models.proof_response import ProofResponse
from typing import List, Dict, Any
from psl_proof.utils.submission import get_historical_chats, ChatHistory, SubmissionChat


def get_uniqueness_score(
    source_chat: SourceChatData,
    chat_histories: List[ChatHistory]
) -> float:
    # Requirement 1: If chat_histories is empty, return 1
    if not chat_histories:
        return 1.0

    chat_ended_on = (
        source_chat.chat_ended_on if source_chat.chat_ended_on else datetime.now()
    )
    # Loop through chat_histories to find a match by source_chat_id
    for history in chat_histories:
        if history.source_chat_id == source_chat.chat_id_as_key():
            # Loop through chat_list to find a match by chat_ended_On date
            for historical_chat in history.chat_list:
                historical_chat_ended_on = historical_chat.chat_ended_on

                if historical_chat_ended_on.tzinfo is not None:
                    # Remove timezone info
                    historical_chat_ended_on = historical_chat_ended_on.replace(tzinfo=None)

                if chat_ended_on.tzinfo is not None:
                    chat_ended_on = chat_ended_on.replace(tzinfo=None)

                time_in_seconds = (chat_ended_on - historical_chat_ended_on).total_seconds()
                time_in_hours = int(time_in_seconds // 3600)
                if time_in_hours < 12: # within 12 Hours..
                    return 0.0

    # If no matching source_chat_id is found, return 1
    return 1.0

def validate_data(
    config: Dict[str, Any],
    cargo_data : CargoData,
    proof_data : ProofResponse
) :
    source_data : SourceChatData = cargo_data.source_data
    source_chats = source_data.source_chats

    total_quality = 0.00
    total_uniqueness = 0.00
    chat_count = 0

    #Validate source data via valiator.api & obtain unquiness
    chat_histories = get_historical_chats(
        config,
        source_data
    )
    #print(f"chat_histories: {chat_histories}")

    # Loop through the chat_data_list
    for source_chat in source_chats:

        #print(f"source_chat:{source_chat}")
        chat_count += 1  # Increment chat count
        source_contents = None
        contents_length = 0
        if source_chat.contents:  # Ensure chat_contents is not None
            source_contents = source_chat.content_as_text()
            #print(f"source_contents: {source_contents}")
            contents_length = len(source_contents)

        if (contents_length > 0):

            chat_id = source_chat.chat_id

            quality = source_chat.quality_score()
            print(f"Chat({chat_id}) - quality: {quality}")

            total_quality += quality

            uniqueness = get_uniqueness_score(
              source_chat,
              chat_histories
            )
            print(f"Chat({chat_id}) - uniqueness: {uniqueness}")
            total_uniqueness += uniqueness

            #print(f"source_contents: {source_contents}")
            #RL: No longer generate data for sentiment & keywords
            # Create a ChatData instance and add it to the list
            #chat_data = ChatData(
            #    chat_length=contents_length,
            #    chat_start_on = source_chat.chat_start_on,
            #    chat_ended_on = source_chat.chat_ended_on
            #)
            #print(f"chat_data: {chat_data}")
            #cargo_data.chat_list.append(
            #    chat_data
            #)

    # Calculate uniqueness if there are chats
    if chat_count > 0:
        proof_data.quality = round(total_quality / chat_count, 2)
        print(f"proof_data.quality: {proof_data.quality}")

        proof_data.uniqueness = round(total_uniqueness / chat_count, 2)
        print(f"proof_data.uniqueness: {proof_data.uniqueness}")