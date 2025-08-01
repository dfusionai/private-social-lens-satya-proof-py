import math
from datetime import datetime

from psl_proof.models.cargo_data import CargoData, ChatData, SourceChatData, SourceData
from psl_proof.models.proof_response import ProofResponse

from typing import List, Dict, Any

from psl_proof.models.submission_dtos import ChatHistory, SubmissionChat, ChatHistory, SubmissionHistory

from psl_proof.utils.open_ai_token import OpenAIToken

#from psl_proof.utils.feature_extraction import get_keywords_keybert, get_sentiment_data

def get_total_score(quality, uniqueness)-> float:
    #total_score = quality # Since uniqueness always 1
    total_score = (quality * 0.5
        + uniqueness * 0.5)

    return total_score

def get_quality_score(
    source_chat: SourceChatData
) -> float:
    #timeliness_value
    timeliness_value = 0
    if source_chat.total_content_length > 0:
        # tav = (𝛴 litsi) / (𝛴 li)
        time_avg = float(source_chat.total_content_value) / float(source_chat.total_content_length)
        # a = ln(2) / thl
        half_life = 600.0  # 600 minutes
        time_decay = math.log(2) / half_life
        # t = exp(-atav)
        timeliness_value = math.exp(- time_decay * time_avg)  # range 0 to 1

    #thoughtfulness_of_conversation
    thoughtfulness_of_conversation = 0.0
    n = len(source_chat.participants)  # n: number of participants
    if n > 1:
        u = 3.0  # 𝜇: optimal number of participants
        d = 5.0  # 𝜎: standard deviation of the curve

        # Formula: p = exp(-(n-𝜇) / (2𝜎^2))
        thoughtfulness_of_conversation = math.exp(-(n - u) / (2 * d ** 2))  # range 0 to 1

    #contextualness_of_conversation
    c = source_chat.total_content_length #total token length, c, of the text data
    m = 2.0 #midpoint
    k = 1.0 #key parameters.
    # l=1/(1+exp(-k(c-c0)))
    contextualness_of_conversation = 1.0/(1.0 + math.exp(-k*(c-m)))

    #quality_score
    a = 1 # factor
    b = 1 # factor
    c = 1 # factor
    t = timeliness_value
    p = thoughtfulness_of_conversation
    l = contextualness_of_conversation
    return (a*t + b*t + c*l)/(a+b+c)


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
            # Loop through chat_list: should be only one the most recent record
            for historical_chat in history.chat_list:

                historical_chat_ended_on = historical_chat.chat_ended_on

                if historical_chat_ended_on.tzinfo is not None:
                    # Remove timezone info
                    historical_chat_ended_on = historical_chat_ended_on.replace(tzinfo=None)

                if chat_ended_on.tzinfo is not None:
                    chat_ended_on = chat_ended_on.replace(tzinfo=None)

                # based on datetime of last entry of conversation/chat
                # determin time different between last submission and current submission
                time_in_seconds = (chat_ended_on - historical_chat_ended_on).total_seconds()
                time_in_hours = int(time_in_seconds // 3600)
                if time_in_hours <= 1 : # within 1 hours
                    return 0.0
                return 1.0 # unique

                #if time_in_hours <= 24: # within 24 Hours..
                #    print(f"time_in_hours:{time_in_hours}")
                #    time_decay = math.log(2) / 12   #half_life: 12hrs, more recent less scores...
                #    return math.exp(-time_decay * (24 - time_in_hours))

    # If no matching source_chat_id is found, return 1
    return 1.0

def validate_data(
    config: Dict[str, Any],
    cargo_data : CargoData,
    proof_data : ProofResponse
) :
    source_data : SourceChatData = cargo_data.source_data
    source_chats = source_data.source_chats

    #Reset valuse
    cargo_data.total_quality = 0.0
    cargo_data.total_uniqueness = 0.0
    chat_count = 0

    scores = []
    # Loop through chat_data_list
    for source_chat in source_chats:
        chat_count += 1
        #print(f"source_chat {chat_count}:{source_chat}")
        source_contents = None
        contents_length = 0
        if source_chat.contents:  # Ensure chat_contents is not None
            source_contents = source_chat.content_as_text()

            #print(f"source_contents: {source_contents}")
            contents_length = len(source_contents)


        if (contents_length > 0):

            quality = get_quality_score(
              source_chat
            )
            uniqueness = get_uniqueness_score(
              source_chat,
              cargo_data.chat_histories
            )

            print(f"Chat {chat_count} >> Quality: {quality} | Uniqueness: {uniqueness}")
            # can not be duplicate data...
            total_score = 0
            if (uniqueness > 0):
                total_score = get_total_score(quality, uniqueness)
                scores.append((quality, uniqueness, total_score))

            try :
                counter = OpenAIToken(model="gpt-4-turbo")
                source_chat.tik_token = counter.count_text_tokens(
                    source_contents
                )
                print(f"Chat {chat_count} >> tik_token: {source_chat.tik_token} ")
            except ValueError as e:
                source_chat.tik_token = 0
                logging.error(f"Chat {chat_count} >> Count tik_token with Error: {e} ")

            #print(f"source_contents: {source_contents}")

            # disable on 27/03/2025
            # chat_sentiment = get_sentiment_data(
            #     source_contents
            # )
            # chat_keywords = get_keywords_keybert(
            #     source_contents
            # )

            # chat_data = ChatData(
            #     chat_length=contents_length,
            #     total_score = total_score,
            #     quality = quality,
            #     uniqueness= uniqueness,
            #     chat_start_on = source_chat.chat_start_on,
            #     chat_ended_on = source_chat.chat_ended_on,
            #     sentiment = chat_sentiment,
            #     keywords = chat_keywords
            # )
            # #print(f"chat_data: {chat_data}")
            # cargo_data.chat_list.append(
            #     chat_data
            # )

    # Sort scores by total_score descending
    sorted_scores = sorted(scores, key=lambda x: x[2], reverse=True)
    # print(f"All Scores count: {len(sorted_scores)}")

    # Determine top_n from config, defaulting to all if not specified
    max_n = config.get('top_n_chats', 50)
    top_n = min(max_n, len(sorted_scores))  # Ensure we don't exceed available entries
    #print(f"top_n: {top_n}")

    # Select top N entries
    selected_scores = sorted_scores[:top_n]
    # print(f"Top {max_n} Scores count: {len(selected_scores)}")


    # Sum the Top N scores
    cargo_data.total_quality = sum(score[0] for score in selected_scores)
    cargo_data.total_uniqueness = sum(score[1] for score in selected_scores)

    # print(f"cargo_data.total_quality: {cargo_data.total_quality}")
    # print(f"cargo_data.total_uniqueness: {cargo_data.total_uniqueness}")