"""Hand-curated labeled examples of cognitive distortions.

Sourced and paraphrased from public CBT materials: David Burns' *Feeling Good*
(the original list of ten distortions, later extended), Greenberger & Padesky's
*Mind Over Mood*, Beck Institute patient worksheets, and the Centre for
Clinical Interventions (CCI, Perth) self-help workbooks. Examples are rewritten
in first-person journal voice so semantic similarity against real journal
entries does useful work — the embedder shouldn't have to bridge a register
gap.

The list is the source of truth. Re-running ``uv run python -m
rag.distortions.seed`` drops and re-embeds the Chroma collection from this
file. Adding or editing entries and re-running is the intended workflow.
"""

from __future__ import annotations

from typing import TypedDict

from schemas import DistortionLabel

from .store import rebuild_collection


class SeedExample(TypedDict):
    id: str
    label: DistortionLabel
    text: str
    explanation: str


SEED_EXAMPLES: list[SeedExample] = [
    # --- catastrophizing -------------------------------------------------
    {
        "id": "catastrophizing_01",
        "label": "catastrophizing",
        "text": "If I bomb this presentation tomorrow my career is finished.",
        "explanation": "A single setback (one bad presentation) is escalated to a permanent, total outcome (career finished).",
    },
    {
        "id": "catastrophizing_02",
        "label": "catastrophizing",
        "text": "My boss didn't reply to my Slack. I'm definitely getting fired by Friday.",
        "explanation": "An ambiguous neutral event (no reply yet) is treated as evidence of the worst possible consequence.",
    },
    {
        "id": "catastrophizing_03",
        "label": "catastrophizing",
        "text": "If I fail this exam I won't graduate, I won't get a job, and my whole life is ruined.",
        "explanation": "A chain of catastrophic conclusions stacked on top of one bounded event.",
    },
    {
        "id": "catastrophizing_04",
        "label": "catastrophizing",
        "text": "My chest feels tight. This must be a heart attack and I'm going to die in this room.",
        "explanation": "A common bodily sensation is interpreted as imminent fatal disaster.",
    },
    {
        "id": "catastrophizing_05",
        "label": "catastrophizing",
        "text": "If she doesn't text back tonight, the relationship is over and I'll be alone forever.",
        "explanation": "A short delay is escalated to permanent abandonment.",
    },
    {
        "id": "catastrophizing_06",
        "label": "catastrophizing",
        "text": "I made a typo in the launch email. The whole campaign is ruined and the team will lose all trust in me.",
        "explanation": "A trivial mistake is treated as a project- and reputation-ending event.",
    },
    {
        "id": "catastrophizing_07",
        "label": "catastrophizing",
        "text": "If this funding round doesn't close, the company dies and everyone on the team will hate me.",
        "explanation": "A possible business setback is forecast as total collapse plus universal personal blame.",
    },
    {
        "id": "catastrophizing_08",
        "label": "catastrophizing",
        "text": "If I admit I don't understand this in the meeting, everyone will realize I'm a fraud and I'll be pushed out.",
        "explanation": "Asking a clarifying question is reframed as an existential professional threat.",
    },
    {
        "id": "catastrophizing_09",
        "label": "catastrophizing",
        "text": "The check engine light came on. The engine is going to seize on the freeway and I'll crash.",
        "explanation": "A maintenance signal is treated as a cinematic worst-case event.",
    },
    {
        "id": "catastrophizing_10",
        "label": "catastrophizing",
        "text": "If I miss this deadline they'll never give me real work again and my career trajectory is dead.",
        "explanation": "A single missed deadline is escalated to permanent professional irrelevance.",
    },
    {
        "id": "catastrophizing_11",
        "label": "catastrophizing",
        "text": "I forgot to send the contract on time. This is going to blow up the entire deal and tank the quarter.",
        "explanation": "A small operational slip is forecast as a quarter-defining failure.",
    },
    {
        "id": "catastrophizing_12",
        "label": "catastrophizing",
        "text": "My kid skinned his knee at the playground. He could get an infection and end up in the hospital.",
        "explanation": "A minor scrape is escalated to a serious medical emergency.",
    },
    # --- all_or_nothing --------------------------------------------------
    {
        "id": "all_or_nothing_01",
        "label": "all_or_nothing",
        "text": "If I can't run the full marathon, there's no point in training at all.",
        "explanation": "Anything short of a perfect outcome is treated as worthless — no middle ground.",
    },
    {
        "id": "all_or_nothing_02",
        "label": "all_or_nothing",
        "text": "I broke my diet at lunch, so the whole day is ruined. I might as well eat whatever I want now.",
        "explanation": "One small slip turns a partial success into total failure.",
    },
    {
        "id": "all_or_nothing_03",
        "label": "all_or_nothing",
        "text": "Either I get the promotion this cycle or I'm a total failure at this company.",
        "explanation": "Career outcomes are forced into a binary: complete success or complete failure.",
    },
    {
        "id": "all_or_nothing_04",
        "label": "all_or_nothing",
        "text": "If I'm not the best engineer on the team, I'm essentially useless here.",
        "explanation": "Anything below the top rank is treated as the bottom — there's no middle of the distribution.",
    },
    {
        "id": "all_or_nothing_05",
        "label": "all_or_nothing",
        "text": "I missed the gym today, so this whole week is wasted.",
        "explanation": "A single missed session collapses an entire week into the 'failed' category.",
    },
    {
        "id": "all_or_nothing_06",
        "label": "all_or_nothing",
        "text": "If I can't fix this perfectly the first time, I shouldn't even start.",
        "explanation": "Any imperfection is treated as equivalent to total failure, blocking action entirely.",
    },
    {
        "id": "all_or_nothing_07",
        "label": "all_or_nothing",
        "text": "He didn't laugh at my joke. He must hate me.",
        "explanation": "A tepid response is read as the maximum negative reaction, with no in-between possible.",
    },
    {
        "id": "all_or_nothing_08",
        "label": "all_or_nothing",
        "text": "Either this essay is brilliant or it's garbage, and right now it's garbage.",
        "explanation": "Quality is forced into two extremes with no middle where most real work lives.",
    },
    {
        "id": "all_or_nothing_09",
        "label": "all_or_nothing",
        "text": "I'm either a great parent or a terrible one, and after today I know which one I am.",
        "explanation": "A complex, ongoing role is reduced to one of two opposed labels based on a single day.",
    },
    {
        "id": "all_or_nothing_10",
        "label": "all_or_nothing",
        "text": "If she's not 100% in, she's out. There's no halfway.",
        "explanation": "A relationship is forced into a binary commitment frame, denying any partial or evolving stance.",
    },
    {
        "id": "all_or_nothing_11",
        "label": "all_or_nothing",
        "text": "The code review found two issues so the whole PR is broken.",
        "explanation": "A few correctable issues collapse the entire piece of work into the 'broken' category.",
    },
    {
        "id": "all_or_nothing_12",
        "label": "all_or_nothing",
        "text": "If I can't quit drinking entirely, there's no point in cutting back at all.",
        "explanation": "A non-perfect harm-reduction path is dismissed as equivalent to doing nothing.",
    },
    # --- emotional_reasoning --------------------------------------------
    {
        "id": "emotional_reasoning_01",
        "label": "emotional_reasoning",
        "text": "I feel like a fraud, so I must actually be one.",
        "explanation": "An internal feeling is taken as direct evidence of an external fact.",
    },
    {
        "id": "emotional_reasoning_02",
        "label": "emotional_reasoning",
        "text": "I feel guilty about saying no, so saying no must have been wrong.",
        "explanation": "Guilt is treated as proof that the behavior causing it was morally bad.",
    },
    {
        "id": "emotional_reasoning_03",
        "label": "emotional_reasoning",
        "text": "I feel anxious walking into the office, so something bad must be about to happen there.",
        "explanation": "Anxiety is treated as accurate forecasting of external danger rather than an internal state.",
    },
    {
        "id": "emotional_reasoning_04",
        "label": "emotional_reasoning",
        "text": "I feel unloved, therefore nobody loves me.",
        "explanation": "A subjective feeling is converted into a universal statement about other people.",
    },
    {
        "id": "emotional_reasoning_05",
        "label": "emotional_reasoning",
        "text": "I feel overwhelmed, so this project must actually be impossible.",
        "explanation": "An emotional state of overwhelm is interpreted as objective evidence about task feasibility.",
    },
    {
        "id": "emotional_reasoning_06",
        "label": "emotional_reasoning",
        "text": "I feel embarrassed remembering what I said, so it must have been humiliating to everyone there.",
        "explanation": "Internal embarrassment is treated as proof of how the moment landed for others.",
    },
    {
        "id": "emotional_reasoning_07",
        "label": "emotional_reasoning",
        "text": "I feel hopeless about my finances, so the situation must really be hopeless.",
        "explanation": "Hopelessness as an emotion is mistaken for an accurate assessment of the situation.",
    },
    {
        "id": "emotional_reasoning_08",
        "label": "emotional_reasoning",
        "text": "I feel jealous, so he must be doing something wrong.",
        "explanation": "Jealousy is treated as evidence of a partner's misbehavior rather than an internal reaction.",
    },
    {
        "id": "emotional_reasoning_09",
        "label": "emotional_reasoning",
        "text": "I feel disgusted with myself, so I really am disgusting.",
        "explanation": "A self-directed emotion is taken as objective proof of personal worth.",
    },
    {
        "id": "emotional_reasoning_10",
        "label": "emotional_reasoning",
        "text": "I feel like the meeting went badly, so it must have gone badly.",
        "explanation": "A felt sense is treated as the verdict, ignoring observable evidence to the contrary.",
    },
    {
        "id": "emotional_reasoning_11",
        "label": "emotional_reasoning",
        "text": "I feel like I'm being judged, so people in this room must be judging me.",
        "explanation": "An internal feeling of being judged is converted into a confident claim about others' minds.",
    },
    {
        "id": "emotional_reasoning_12",
        "label": "emotional_reasoning",
        "text": "I'm scared to fly, so flying must actually be dangerous.",
        "explanation": "Fear is treated as a calibrated risk estimate of base-rate probability.",
    },
    # --- mind_reading ----------------------------------------------------
    {
        "id": "mind_reading_01",
        "label": "mind_reading",
        "text": "She didn't say hi this morning. She must be angry at me about last night.",
        "explanation": "Another person's internal state is asserted with confidence from a single ambiguous behavior.",
    },
    {
        "id": "mind_reading_02",
        "label": "mind_reading",
        "text": "He thinks my ideas are stupid, I can tell.",
        "explanation": "A specific mental content is attributed to another person without any direct evidence.",
    },
    {
        "id": "mind_reading_03",
        "label": "mind_reading",
        "text": "Everyone in that meeting was thinking I didn't belong there.",
        "explanation": "A confident inference about an entire group's thoughts, drawn from no observable cue.",
    },
    {
        "id": "mind_reading_04",
        "label": "mind_reading",
        "text": "My manager hasn't said anything about my work lately. He must be disappointed in me.",
        "explanation": "Silence is interpreted as a specific negative judgment rather than as silence.",
    },
    {
        "id": "mind_reading_05",
        "label": "mind_reading",
        "text": "My friend canceled dinner. She's clearly tired of me.",
        "explanation": "A scheduling change is read as evidence of a hidden, durable negative attitude.",
    },
    {
        "id": "mind_reading_06",
        "label": "mind_reading",
        "text": "When the room went quiet after I spoke, I knew they all thought I was wrong.",
        "explanation": "Silence is treated as a unanimous mental verdict from the audience.",
    },
    {
        "id": "mind_reading_07",
        "label": "mind_reading",
        "text": "He's smiling but I can tell he's actually furious with me underneath.",
        "explanation": "An overriding hidden emotional state is attributed to someone in spite of contrary outward behavior.",
    },
    {
        "id": "mind_reading_08",
        "label": "mind_reading",
        "text": "She didn't compliment my outfit, so she must think I look terrible.",
        "explanation": "Absence of a positive comment is interpreted as a present, specific negative judgment.",
    },
    {
        "id": "mind_reading_09",
        "label": "mind_reading",
        "text": "The interviewer crossed her arms. She's already decided she doesn't want to hire me.",
        "explanation": "Body language is read as a final, specific conclusion about the person's hiring intent.",
    },
    {
        "id": "mind_reading_10",
        "label": "mind_reading",
        "text": "Nobody has reacted to my message in the group chat. They all think it was a dumb thing to say.",
        "explanation": "A delay in responses is interpreted as a unanimous shared judgment about the message.",
    },
    {
        "id": "mind_reading_11",
        "label": "mind_reading",
        "text": "He keeps checking his phone. He's bored of this conversation with me.",
        "explanation": "A common behavior is assigned a specific motivational meaning without evidence.",
    },
    {
        "id": "mind_reading_12",
        "label": "mind_reading",
        "text": "I just know my coworkers are talking about how slow I am behind my back.",
        "explanation": "A complete narrative about other people's private conversations is asserted with no direct knowledge.",
    },
    # --- fortune_telling -------------------------------------------------
    {
        "id": "fortune_telling_01",
        "label": "fortune_telling",
        "text": "I know I'm going to fail this interview tomorrow.",
        "explanation": "A specific future negative outcome is asserted with certainty before any evidence exists.",
    },
    {
        "id": "fortune_telling_02",
        "label": "fortune_telling",
        "text": "There's no point applying — they're definitely not going to pick me.",
        "explanation": "A predicted rejection is treated as a foregone conclusion that justifies not even trying.",
    },
    {
        "id": "fortune_telling_03",
        "label": "fortune_telling",
        "text": "If I go to the party I'll just stand awkwardly in the corner all night.",
        "explanation": "A detailed bad future is forecast as if already observed.",
    },
    {
        "id": "fortune_telling_04",
        "label": "fortune_telling",
        "text": "This relationship is going to end the same way the last one did.",
        "explanation": "A confident prediction of a specific future based on pattern-matching to one prior case.",
    },
    {
        "id": "fortune_telling_05",
        "label": "fortune_telling",
        "text": "I'll never find another job that pays this well.",
        "explanation": "A permanent negative future is asserted as if it has already been confirmed.",
    },
    {
        "id": "fortune_telling_06",
        "label": "fortune_telling",
        "text": "I'm going to forget my lines on stage and the whole audience will see me freeze.",
        "explanation": "A specific embarrassing scene is forecast in detail before the event.",
    },
    {
        "id": "fortune_telling_07",
        "label": "fortune_telling",
        "text": "Even if I send the pitch, they're not going to read it. They never read pitches.",
        "explanation": "A confident prediction about a future behavior of others, presented as a hard rule.",
    },
    {
        "id": "fortune_telling_08",
        "label": "fortune_telling",
        "text": "I just know I'm going to mess this up the moment I open my mouth.",
        "explanation": "A negative future event is treated as certain rather than as one possibility among many.",
    },
    {
        "id": "fortune_telling_09",
        "label": "fortune_telling",
        "text": "Even if I get the job, I'll burn out within six months and have to quit anyway.",
        "explanation": "A multi-step negative future is mapped out and treated as inevitable.",
    },
    {
        "id": "fortune_telling_10",
        "label": "fortune_telling",
        "text": "I'm going to spend my whole weekend stressing about Monday and ruin it.",
        "explanation": "The future is foreclosed as a specific bad experience before it has begun.",
    },
    {
        "id": "fortune_telling_11",
        "label": "fortune_telling",
        "text": "If I bring this up, the conversation is going to turn into a huge fight.",
        "explanation": "A predicted conflict outcome is presented as certain, often used to justify avoidance.",
    },
    {
        "id": "fortune_telling_12",
        "label": "fortune_telling",
        "text": "Why bother going to the doctor? They're just going to tell me there's nothing wrong.",
        "explanation": "A predicted dismissive future response is asserted as fact, used as a reason to skip the action.",
    },
    # --- personalization -------------------------------------------------
    {
        "id": "personalization_01",
        "label": "personalization",
        "text": "My team missed the quarter and it's all because of me.",
        "explanation": "A multi-cause team outcome is attributed entirely to the speaker's personal contribution.",
    },
    {
        "id": "personalization_02",
        "label": "personalization",
        "text": "My friend is in a bad mood today. I must have done something to upset her.",
        "explanation": "Another person's mood is assumed to be caused by the speaker, despite many other possible causes.",
    },
    {
        "id": "personalization_03",
        "label": "personalization",
        "text": "My son got a bad grade. I'm clearly a failure as a parent.",
        "explanation": "A child's outcome is read as a direct verdict on the parent's worth.",
    },
    {
        "id": "personalization_04",
        "label": "personalization",
        "text": "The party was awkward — that was my fault for inviting too many people.",
        "explanation": "Excessive personal responsibility is taken for a complex social outcome with many contributors.",
    },
    {
        "id": "personalization_05",
        "label": "personalization",
        "text": "If I'd been a better partner, he wouldn't have started drinking again.",
        "explanation": "Another adult's behavior is attributed entirely to the speaker's failures.",
    },
    {
        "id": "personalization_06",
        "label": "personalization",
        "text": "The deal fell through because I didn't push hard enough on the call.",
        "explanation": "A multi-party business outcome is collapsed into a single self-blaming cause.",
    },
    {
        "id": "personalization_07",
        "label": "personalization",
        "text": "My boss seems stressed today. He's probably annoyed with my work specifically.",
        "explanation": "A general state in another person is read as being specifically about the speaker.",
    },
    {
        "id": "personalization_08",
        "label": "personalization",
        "text": "The kids are acting out at school because I work too much.",
        "explanation": "Complex behavioral causes are reduced to a single self-blaming explanation.",
    },
    {
        "id": "personalization_09",
        "label": "personalization",
        "text": "Two people left the company last month. I should have done something to keep them.",
        "explanation": "Decisions belonging to other adults are framed as the speaker's personal failure to act.",
    },
    {
        "id": "personalization_10",
        "label": "personalization",
        "text": "She's quiet at dinner. It must be because of what I said earlier.",
        "explanation": "Another person's behavior is assumed to revolve around the speaker, ignoring alternative causes.",
    },
    {
        "id": "personalization_11",
        "label": "personalization",
        "text": "If I'd noticed the bug in code review, prod wouldn't have gone down. This outage is on me.",
        "explanation": "A systemic failure with many contributing factors is fully internalized as personal fault.",
    },
    {
        "id": "personalization_12",
        "label": "personalization",
        "text": "My friend didn't get the job. I should have introduced him to more people in my network.",
        "explanation": "Another person's hiring outcome is treated as a moral failing of the speaker's networking effort.",
    },
    # --- should_statements -----------------------------------------------
    {
        "id": "should_statements_01",
        "label": "should_statements",
        "text": "I should be further along in my career by now.",
        "explanation": "A vague comparative standard is applied with 'should', generating self-criticism without a clear referent.",
    },
    {
        "id": "should_statements_02",
        "label": "should_statements",
        "text": "I shouldn't feel this tired. I'm not even doing that much.",
        "explanation": "A normative rule is applied to one's own emotional and physical state.",
    },
    {
        "id": "should_statements_03",
        "label": "should_statements",
        "text": "I have to respond to every email the same day or I'm letting people down.",
        "explanation": "A self-imposed absolute rule produces shame whenever it is broken.",
    },
    {
        "id": "should_statements_04",
        "label": "should_statements",
        "text": "I must always be the one who keeps the family in touch.",
        "explanation": "An absolute role obligation is asserted that no actual rule requires.",
    },
    {
        "id": "should_statements_05",
        "label": "should_statements",
        "text": "He should know how I feel without me having to say it.",
        "explanation": "A 'should' is directed at another person, generating resentment when the implicit rule is broken.",
    },
    {
        "id": "should_statements_06",
        "label": "should_statements",
        "text": "I should be over this breakup by now. It's been months.",
        "explanation": "A timeline rule is applied to grief, generating shame about the natural pace of recovery.",
    },
    {
        "id": "should_statements_07",
        "label": "should_statements",
        "text": "I have to hit the gym every single day or I'm being lazy.",
        "explanation": "An absolute rule converts any deviation into a moral failing.",
    },
    {
        "id": "should_statements_08",
        "label": "should_statements",
        "text": "I shouldn't need help with this. I should be able to figure it out alone.",
        "explanation": "A 'should' makes asking for help feel like evidence of inadequacy.",
    },
    {
        "id": "should_statements_09",
        "label": "should_statements",
        "text": "She should have known that comment would hurt me.",
        "explanation": "An external 'should' attributes a duty that was never communicated, producing anger when it isn't met.",
    },
    {
        "id": "should_statements_10",
        "label": "should_statements",
        "text": "I shouldn't be this anxious about something so small.",
        "explanation": "A self-applied rule about feelings turns the original emotion into compounded guilt.",
    },
    {
        "id": "should_statements_11",
        "label": "should_statements",
        "text": "I have to read every paper in this field or I'm not a serious researcher.",
        "explanation": "An absolute and unattainable standard generates ongoing self-criticism.",
    },
    {
        "id": "should_statements_12",
        "label": "should_statements",
        "text": "I must keep the house spotless or I'm failing as an adult.",
        "explanation": "A rigid domestic standard is treated as a measure of personal worth.",
    },
    # --- labeling --------------------------------------------------------
    {
        "id": "labeling_01",
        "label": "labeling",
        "text": "I missed the deadline. I'm such a loser.",
        "explanation": "A behavior is converted into a global, fixed identity label.",
    },
    {
        "id": "labeling_02",
        "label": "labeling",
        "text": "I forgot her birthday. I'm a terrible friend.",
        "explanation": "One forgotten event is treated as defining the entire friendship identity.",
    },
    {
        "id": "labeling_03",
        "label": "labeling",
        "text": "I can never get the math right on these. I'm an idiot.",
        "explanation": "A repeated specific difficulty is generalized into an identity label about intelligence.",
    },
    {
        "id": "labeling_04",
        "label": "labeling",
        "text": "He cut me off in traffic. What a complete asshole.",
        "explanation": "One behavior is used to assign a fixed, total identity label to another person.",
    },
    {
        "id": "labeling_05",
        "label": "labeling",
        "text": "I lost my temper with the kids again. I'm a horrible parent.",
        "explanation": "An incident of dysregulation is converted into a sweeping identity statement about parenting.",
    },
    {
        "id": "labeling_06",
        "label": "labeling",
        "text": "I cried in the meeting. I'm so weak.",
        "explanation": "A momentary emotional response is recast as a permanent character trait.",
    },
    {
        "id": "labeling_07",
        "label": "labeling",
        "text": "She voted for that party? She's a moron.",
        "explanation": "One opinion is used to assign a global, fixed identity label to another person.",
    },
    {
        "id": "labeling_08",
        "label": "labeling",
        "text": "I drank too much last night. I'm a complete mess of a person.",
        "explanation": "One night's behavior is converted into an identity-level summary of the self.",
    },
    {
        "id": "labeling_09",
        "label": "labeling",
        "text": "I can't even keep a houseplant alive. I'm a failure at everything.",
        "explanation": "A trivial domain-specific lapse is generalized into a global identity verdict.",
    },
    {
        "id": "labeling_10",
        "label": "labeling",
        "text": "He didn't text me back for three days. He's such a jerk.",
        "explanation": "A specific behavior is used to assign a sweeping identity label to another person.",
    },
    {
        "id": "labeling_11",
        "label": "labeling",
        "text": "I procrastinated all afternoon. I'm just lazy.",
        "explanation": "One afternoon of avoidance is used to define a stable personality trait.",
    },
    {
        "id": "labeling_12",
        "label": "labeling",
        "text": "I keep getting nervous in social situations. I'm just a fundamentally awkward person.",
        "explanation": "A pattern of feelings is reified into a permanent identity label.",
    },
    # --- magnification_minimization -------------------------------------
    {
        "id": "magnification_minimization_01",
        "label": "magnification_minimization",
        "text": "Sure I shipped the feature on time, but anyone could have done it. The one bug I missed is what really matters.",
        "explanation": "A real accomplishment is shrunk while a small error is enlarged into the dominant story.",
    },
    {
        "id": "magnification_minimization_02",
        "label": "magnification_minimization",
        "text": "Yes I got promoted, but the raise was tiny. The real story is that they don't actually value me.",
        "explanation": "The positive (promotion) is minimized; a chosen negative reading is amplified into the truth.",
    },
    {
        "id": "magnification_minimization_03",
        "label": "magnification_minimization",
        "text": "I aced the exam, but it was an easy one. The B+ in the other class is what defines this semester.",
        "explanation": "Successes are shrunk by attributing them to easy conditions while the smaller setback is enlarged.",
    },
    {
        "id": "magnification_minimization_04",
        "label": "magnification_minimization",
        "text": "I closed three deals this month, but I lost the big one. That's the only one that counts.",
        "explanation": "Multiple wins are minimized; one loss is magnified into the only metric that matters.",
    },
    {
        "id": "magnification_minimization_05",
        "label": "magnification_minimization",
        "text": "Everyone said the talk went well, but I stumbled on one slide. That stumble is what they'll remember.",
        "explanation": "Broad positive feedback is minimized; one self-noticed flaw is enlarged into the public takeaway.",
    },
    {
        "id": "magnification_minimization_06",
        "label": "magnification_minimization",
        "text": "I lost ten pounds, but I'm still way bigger than I want to be. The progress doesn't really count.",
        "explanation": "Visible progress is shrunk while the remaining gap is enlarged.",
    },
    {
        "id": "magnification_minimization_07",
        "label": "magnification_minimization",
        "text": "He apologized, but it took him too long to do it. The apology doesn't really mean anything now.",
        "explanation": "A genuine positive action is shrunk while a secondary complaint is magnified.",
    },
    {
        "id": "magnification_minimization_08",
        "label": "magnification_minimization",
        "text": "Nine out of ten reviews loved my book, but the one negative review is the one I keep rereading.",
        "explanation": "Positive feedback is treated as background noise; one negative is magnified into the signal.",
    },
    {
        "id": "magnification_minimization_09",
        "label": "magnification_minimization",
        "text": "I helped my friend move all weekend, but I wasn't as fast as her brother. That's all I can think about.",
        "explanation": "A clear contribution is minimized; an unflattering comparison is enlarged into the dominant memory.",
    },
    {
        "id": "magnification_minimization_10",
        "label": "magnification_minimization",
        "text": "My salary doubled but my old college roommate makes more than me. That's the only number that matters.",
        "explanation": "Real personal progress is shrunk; an external comparison is enlarged into the only meaningful measure.",
    },
    {
        "id": "magnification_minimization_11",
        "label": "magnification_minimization",
        "text": "I ran my best 5K time ever, but the front of the pack was minutes ahead of me. My time doesn't really matter.",
        "explanation": "A personal best is minimized while distance from the leaders is amplified into the verdict.",
    },
    {
        "id": "magnification_minimization_12",
        "label": "magnification_minimization",
        "text": "Sales are up 30% this year, but our competitor grew 35%. Honestly we're losing.",
        "explanation": "Strong absolute progress is shrunk against a marginal external delta that is then enlarged.",
    },
    # --- mental_filter ---------------------------------------------------
    {
        "id": "mental_filter_01",
        "label": "mental_filter",
        "text": "The retro had a lot of praise but one person said my comms were unclear. That's the only thing I can think about.",
        "explanation": "Attention sticks to the single negative item while the wider positive context is filtered out.",
    },
    {
        "id": "mental_filter_02",
        "label": "mental_filter",
        "text": "Most of the day was actually fine, but that one rude comment from the cashier is what I keep replaying.",
        "explanation": "An overall neutral or positive day is overshadowed by selective focus on one negative moment.",
    },
    {
        "id": "mental_filter_03",
        "label": "mental_filter",
        "text": "The whole vacation was great except for one bad dinner, and that's somehow the trip I remember.",
        "explanation": "A selective focus on one negative event reshapes the entire memory of the experience.",
    },
    {
        "id": "mental_filter_04",
        "label": "mental_filter",
        "text": "Forty people clapped at my talk and one person looked bored. All I noticed was the bored person.",
        "explanation": "Attention zooms in on a single negative cue and excludes the much larger positive signal.",
    },
    {
        "id": "mental_filter_05",
        "label": "mental_filter",
        "text": "We had a good week as a team but I can't stop thinking about the one Slack message that didn't land right.",
        "explanation": "A wider pattern is filtered out so a single negative episode dominates the mental picture.",
    },
    {
        "id": "mental_filter_06",
        "label": "mental_filter",
        "text": "My partner did so many sweet things this week, but the one snippy comment is what's stuck in my head.",
        "explanation": "Selective focus on one negative behavior crowds out the surrounding positive ones.",
    },
    {
        "id": "mental_filter_07",
        "label": "mental_filter",
        "text": "There were five questions in the Q&A and four were thoughtful. The one hostile question is the only one I'm replaying.",
        "explanation": "Attention narrows to the one negative interaction while the broader positive ones are filtered out.",
    },
    {
        "id": "mental_filter_08",
        "label": "mental_filter",
        "text": "I keep going back to that one mistake in my code review even though the overall feedback was strong.",
        "explanation": "A selective focus on the one negative comment defines the experience.",
    },
    {
        "id": "mental_filter_09",
        "label": "mental_filter",
        "text": "Most of the meeting went well but my voice cracked once and that's all I can remember.",
        "explanation": "A single self-perceived flaw becomes the entire memory while broader content drops out.",
    },
    {
        "id": "mental_filter_10",
        "label": "mental_filter",
        "text": "The party was fun for hours but I keep replaying the awkward five minutes by the kitchen.",
        "explanation": "A short negative episode is treated as the defining feature of an otherwise enjoyable event.",
    },
    {
        "id": "mental_filter_11",
        "label": "mental_filter",
        "text": "My quarterly review was mostly glowing but I can only see the one improvement area.",
        "explanation": "Positive content is filtered out, leaving only the one negative item to focus on.",
    },
    {
        "id": "mental_filter_12",
        "label": "mental_filter",
        "text": "The report has nine clean pages and one with a typo. I can't stop seeing the typo.",
        "explanation": "Attention fixates on a tiny flaw while the large surrounding correctness goes unnoticed.",
    },
    # --- disqualifying_positive ------------------------------------------
    {
        "id": "disqualifying_positive_01",
        "label": "disqualifying_positive",
        "text": "She said she liked my presentation, but she was just being nice.",
        "explanation": "A positive piece of feedback is dismissed by reattributing it to politeness.",
    },
    {
        "id": "disqualifying_positive_02",
        "label": "disqualifying_positive",
        "text": "Yeah I got an A, but the prof gives everyone A's. It doesn't really mean anything.",
        "explanation": "A positive outcome is rationalized away by attributing it to lax standards rather than effort or skill.",
    },
    {
        "id": "disqualifying_positive_03",
        "label": "disqualifying_positive",
        "text": "Sure I got the offer, but they were desperate to fill the role. It's not because I'm any good.",
        "explanation": "Personal credit for a positive result is reattributed to external desperation.",
    },
    {
        "id": "disqualifying_positive_04",
        "label": "disqualifying_positive",
        "text": "He told me I look great today, but he probably says that to everyone.",
        "explanation": "A specific compliment is dismissed by treating it as generic and meaningless.",
    },
    {
        "id": "disqualifying_positive_05",
        "label": "disqualifying_positive",
        "text": "I shipped the project on time, but anyone with my resources could have done it.",
        "explanation": "Personal contribution is dismissed by claiming the success required no real skill.",
    },
    {
        "id": "disqualifying_positive_06",
        "label": "disqualifying_positive",
        "text": "I made it through the marathon, but I had to walk parts of it, so it doesn't really count.",
        "explanation": "A real achievement is disqualified through a self-imposed purity rule.",
    },
    {
        "id": "disqualifying_positive_07",
        "label": "disqualifying_positive",
        "text": "My therapist says I'm making progress, but she has to say things like that — it's her job.",
        "explanation": "Encouraging feedback is dismissed by attributing it to a professional role obligation.",
    },
    {
        "id": "disqualifying_positive_08",
        "label": "disqualifying_positive",
        "text": "Yes the launch went well, but it was easy mode — the bar was set really low.",
        "explanation": "A success is reframed as not really a success because the conditions were favorable.",
    },
    {
        "id": "disqualifying_positive_09",
        "label": "disqualifying_positive",
        "text": "She said yes to a second date, but probably only because there's nobody else around.",
        "explanation": "A positive social signal is reattributed to scarcity rather than genuine interest.",
    },
    {
        "id": "disqualifying_positive_10",
        "label": "disqualifying_positive",
        "text": "My boss praised my work, but she was probably just trying to keep morale up.",
        "explanation": "Praise is dismissed by attributing it to a managerial tactic rather than genuine evaluation.",
    },
    {
        "id": "disqualifying_positive_11",
        "label": "disqualifying_positive",
        "text": "I lost the weight, but I'll just gain it back, so what's the point in counting it?",
        "explanation": "A current success is preemptively disqualified by predicting it will be undone.",
    },
    {
        "id": "disqualifying_positive_12",
        "label": "disqualifying_positive",
        "text": "He said the book changed his life, but he says that about every book he reads.",
        "explanation": "A specific positive endorsement is dismissed as meaningless through generalization.",
    },
    # --- overgeneralization ---------------------------------------------
    {
        "id": "overgeneralization_01",
        "label": "overgeneralization",
        "text": "Nothing I send out ever lands. Every cold email I write disappears into a void.",
        "explanation": "A category of negative outcomes is generalized using absolute quantifiers ('nothing', 'every', 'ever').",
    },
    {
        "id": "overgeneralization_02",
        "label": "overgeneralization",
        "text": "I always mess things up when it counts.",
        "explanation": "A specific pattern is generalized into a universal rule about the self with 'always'.",
    },
    {
        "id": "overgeneralization_03",
        "label": "overgeneralization",
        "text": "Every guy I date turns out to be a flake.",
        "explanation": "A small sample of negative cases is generalized to an entire category of people.",
    },
    {
        "id": "overgeneralization_04",
        "label": "overgeneralization",
        "text": "Nobody ever wants to hang out with me anymore.",
        "explanation": "Recent friction is generalized into a sweeping universal claim with 'nobody' and 'ever'.",
    },
    {
        "id": "overgeneralization_05",
        "label": "overgeneralization",
        "text": "Every time I try to learn something new I give up halfway through.",
        "explanation": "A general pattern is asserted with 'every time' from a few past examples.",
    },
    {
        "id": "overgeneralization_06",
        "label": "overgeneralization",
        "text": "Job interviews never go well for me.",
        "explanation": "A category-level negative claim is asserted from a few specific outcomes.",
    },
    {
        "id": "overgeneralization_07",
        "label": "overgeneralization",
        "text": "Whenever I open up to someone, they end up using it against me.",
        "explanation": "A 'whenever / always' rule is built from a small set of disappointing past experiences.",
    },
    {
        "id": "overgeneralization_08",
        "label": "overgeneralization",
        "text": "Every recruiter I talk to ghosts me eventually.",
        "explanation": "A specific subset of disappointing interactions is generalized to all of them.",
    },
    {
        "id": "overgeneralization_09",
        "label": "overgeneralization",
        "text": "I never get picked for the interesting projects.",
        "explanation": "A pattern is asserted as a universal rule using 'never'.",
    },
    {
        "id": "overgeneralization_10",
        "label": "overgeneralization",
        "text": "Everyone in tech is fake — they're all just networking at you.",
        "explanation": "An entire community is collapsed into one negative descriptor based on limited encounters.",
    },
    {
        "id": "overgeneralization_11",
        "label": "overgeneralization",
        "text": "All my friendships fall apart eventually. It's just what happens.",
        "explanation": "A handful of past endings is generalized into an inevitable rule about all relationships.",
    },
    {
        "id": "overgeneralization_12",
        "label": "overgeneralization",
        "text": "I can never finish anything I start.",
        "explanation": "A pattern is asserted as a universal personal trait using 'never' and 'anything'.",
    },
]


def main() -> None:
    print(f"Seeding distortions collection with {len(SEED_EXAMPLES)} examples...")
    by_label: dict[str, int] = {}
    for ex in SEED_EXAMPLES:
        by_label[ex["label"]] = by_label.get(ex["label"], 0) + 1
    for label, count in sorted(by_label.items()):
        print(f"  {label}: {count}")

    rebuild_collection(SEED_EXAMPLES)
    print("Done. Collection persisted under backend/data/chroma/distortions/.")


if __name__ == "__main__":
    main()
