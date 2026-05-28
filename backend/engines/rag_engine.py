# rag_engine.py
# RAG Engine module for retrieving knowledge and generating structured workflows using Gemini.

import os
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
import google.genai as genai
# pyrefly: ignore [missing-import]
from google.genai import types as genai_types
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()


def load_vectorstore(db_path: str = None):
    """Load ChromaDB vector store from local filesystem."""
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    embedding_model = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), "..", "database", "chroma_db")
        
    vectorstore = Chroma(
        persist_directory=db_path,
        embedding_function=embedding_model
    )
    return vectorstore

# Local Offline Fallback Diagnoses for 503/429 API failures
FALLBACK_DIAGNOSES = {
    "battery": {
        "causes": "1. Faulty AC Power Adapter: The charging cable or connector may have internal wiring damage.\n2. Degraded Li-ion Battery: The battery cell has chemically degraded over time and can no longer hold voltage.\n3. Loose Internal Power Connector: The battery's motherboard power socket connector has popped slightly loose.\n4. Corrupted Power ACPI Drivers: A operating system software glitch in power management configuration.",
        "fixes": "### Fix 1: Basic Power & Battery Reseat Troubleshooting [EASY]\n**Tools Required:** Multimeter (optional), known compatible AC adapter\n1. Ensure the AC adapter is securely plugged into both a working wall outlet and the laptop's DC power jack.\n2. Turn off the computer completely and disconnect the AC adapter.\n3. Carefully remove the battery from its compartment (if external) or disconnect its cable from the motherboard.\n4. Reconnect the AC adapter and try to power on the laptop, observing the charging indicator.\n\n### Fix 2: Replace the Laptop Battery [MEDIUM]\n**Tools Required:** Small Phillips screwdriver, plastic spudger\n1. Purchase a new, compatible battery specifically designed for your laptop model.\n2. Turn off the laptop, disconnect the AC adapter, and unscrew the bottom case cover.\n3. Carefully disconnect the battery's motherboard cable and remove any mounting screws.\n4. Install the new replacement battery, tighten screws, and refasten the back panel.",
        "verdict": "✅ USER CAN FIX THIS\n\nPower supply and battery replacement are standard modular procedures that can be safely done at home with basic precision screwdrivers.",
        "tips": "1. Avoid leaving the laptop plugged into the charger at 100% capacity continuously.\n2. Keep your device on flat, hard surfaces to prevent battery overheating."
    },
    "fan": {
        "causes": "1. Heavy Dust Accumulation: Dirt and debris clogging the fan blades and copper heatsink fins, blocking airflow.\n2. Dried CPU/GPU Thermal Paste: The thermal conductive interface paste has dried up, resulting in extreme overheating.\n3. Defective Cooling Fan Motor: The internal bearing has failed, causing grinding noises or complete fan seizure.",
        "fixes": "### Fix 1: Clean Fan and Copper Air Vents [EASY]\n**Tools Required:** Compressed air can, soft brush, microfiber cloth\n1. Turn off the device, unplug the power charger, and unscrew the back case.\n2. Locate the fan and hold the blades down gently with a finger to prevent spinning damage.\n3. Use short bursts of compressed air to clear out built-up dust from the fan and copper exhaust radiator.\n\n### Fix 2: Apply CPU & GPU Thermal Paste [HARD]\n**Tools Required:** High-performance thermal paste, isopropyl alcohol, cotton swabs, Phillips screwdriver\n1. Carefully unscrew the copper heatsink pipe assembly in diagonal order.\n2. Clean off all old, dried thermal compound using cotton swabs dipped in isopropyl alcohol.\n3. Apply a small pea-sized drop of thermal paste to the center of the CPU/GPU silicon die.\n4. Re-mount the heatsink assembly and screw it down firmly in diagonal sequence.",
        "verdict": "🏥 GO TO SERVICE CENTER\n\nWhile cleaning dust is an easy fix, removing heatsinks and applying fresh thermal paste requires expert precision to prevent motherboard cracking.",
        "tips": "1. Periodically blow out air vents with compressed air to prevent thermal dust blankets.\n2. Monitor device temperatures under heavy load using free utility apps."
    },
    "ssd": {
        "causes": "1. Loose Storage Drive Connection: The M.2 NVMe card or SATA slot cable has shifted out of place from a drop.\n2. Damaged File System Sectors: Corrupted operating system boot sectors preventing normal startup sequence.\n3. SSD Controller Failure: The flash controller on the drive has suffered thermal damage and failed.",
        "fixes": "### Fix 1: Reseat the M.2 NVMe SSD Drive [EASY]\n**Tools Required:** Small Phillips screwdriver, cleaning eraser\n1. Completely power down the device and remove the bottom motherboard cover.\n2. Locate the M.2 SSD slot, remove the single locking retention screw, and slide the SSD out.\n3. Clean the gold connector contact pins gently with a clean pencil eraser.\n4. Re-insert the SSD firmly into its slot, screw it down, and power on to check.",
        "verdict": "✅ USER CAN FIX THIS\n\nReseating or replacing a standard storage drive is highly modular and takes less than 10 minutes.",
        "tips": "1. Enable automatic cloud backups for all your important personal and work files.\n2. Run regular drive health check utility scans to spot failures early."
    },
    "ram": {
        "causes": "1. Dirty Gold Latch Terminals: Micron dust layers or copper oxidation forming between RAM pins and the slot.\n2. Unseated SO-DIMM Latch: The metal lock springs have loosened, letting the memory card slide out.\n3. Damaged Memory Block Sector: Physical hardware block failure causing crashes or system bios beep codes.",
        "fixes": "### Fix 1: Reseat and Clean the RAM Sticks [EASY]\n**Tools Required:** Soft pencil eraser, clean microfiber cloth\n1. Disconnect the power charger, shut down the device, and open the back cover.\n2. Release the two metal side latches to let the RAM stick spring up at an angle, then pull it out.\n3. Rub the gold contact connectors gently with a pencil eraser to remove oxidation layer.\n4. Re-insert the memory stick firmly into the slot at an angle and push down until it clicks into the metal locks.",
        "verdict": "✅ USER CAN FIX THIS\n\nMemory troubleshooting and upgrades are perfectly safe for beginners and do not require heavy technical skills.",
        "tips": "1. Avoid touching the gold contacts with bare fingers to prevent static electricity discharge.\n2. Ensure purchased upgrade sticks match the exact speed frequency of the motherboard bios."
    },
    "general": {
        "causes": "1. Loose Ribbon Connectors: Minor ribbon cables connecting components have shifted slightly.\n2. Overloaded Bios State: Motherboard CMOS battery holding corrupted static charge.\n3. Physical Wire Corrosion: Fine debris or moisture causing minor circuit shorting.",
        "fixes": "### Fix 1: Perform a Motherboard Hard Reset [EASY]\n**Tools Required:** None\n1. Turn off the device, unplug the power adapter, and remove the battery.\n2. Press and hold the power button down for 30 full seconds to discharge remaining static.\n3. Re-plug only the AC power charger, try to boot, and re-insert the battery afterward.\n\n### Fix 2: Reseat All Internal Ribbon Cables [MEDIUM]\n**Tools Required:** Plastic spudger, tweezers\n1. Open the device chassis and locate major ribbon connectors (keyboard, display, mouse pad).\n2. Flip up the small black retaining locks on the ribbon slots and gently pull out the ribbons.\n3. Inspect pins, re-insert them completely straight, and lock the retaining clip down.",
        "verdict": "🏥 GO TO SERVICE CENTER\n\nComplex motherboard shorts or diagnostics are best analyzed by a certified professional technician.",
        "tips": "1. Never operate your laptops or electronics in highly damp or extremely dusty conditions.\n2. Invest in a simple surge protector outlet to shield your devices from electrical spikes."
    }
}

def run_rag_diagnosis(user_issue: str, vision_analysis: str, detected_components: list[str], ocr_context: str, vectorstore) -> dict:
    """Retrieve relevant docs from ChromaDB and generate structured diagnosis using Gemini 2.5 Flash with safe offline fallbacks."""
    
    # ── PATH A: Standard Online Gemini Generation ───────────
    try:
        # Build combined query combining issue description, yolo-detected parts, and OCR text
        components_str = ", ".join(detected_components) if detected_components else "None"
        combined_query = f"{user_issue}. Components: {components_str}. OCR readings: {ocr_context[:200]}. Vision: {vision_analysis[:200]}"

        # Retrieve relevant documents from Chroma
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(combined_query)
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])

        diagnosis_prompt = f"""
        You are RepairAI, an expert device repair assistant.
        
        USER'S REPORTED ISSUE:
        {user_issue}
        
        YOLO DETECTED COMPONENTS (Visual object detection):
        {components_str}
        
        OCR TEXT EXTRACTION (Text markings and labels read from components):
        {ocr_context}
        
        GENERAL IMAGE VISION ANALYSIS (AI description of visual state):
        {vision_analysis}
        
        RETRIEVED REPAIR KNOWLEDGE BASE (Verified repair guides and manuals):
        {context}
        
        Based on all the above information, generate a STRUCTURED DIAGNOSIS REPORT.
        
        Return your response in EXACTLY this format. You MUST use these exact ALL-CAPS headers, otherwise the system will crash:
        
        ## POSSIBLE CAUSES
        List 3-5 most likely causes of the issue, ordered from most to least likely.
        For each cause, briefly explain why it could be responsible.
        
        ## RECOMMENDED FIXES
        Provide the repair workflows for the causes using this EXACT markdown structure:
        
        ### Fix 1: [Name of the fix] [EASY/MEDIUM/HARD]
        **Tools Required:** [Comma separated list of tools or "None"]
        1. [First action step]
        2. [Second action step]
        
        ### Fix 2: [Name of the fix] [EASY/MEDIUM/HARD]
        **Tools Required:** [Comma separated list of tools]
        1. [First action step]
        2. [Second action step]
        
        ## VERDICT
        Start with either:
        ✅ USER CAN FIX THIS — if the issue can be resolved by the user at home
        🏥 GO TO SERVICE CENTER — if professional repair is required
        
        Then explain the reasoning for your verdict in 2-3 sentences.
        If user can fix it, mention the approximate cost of parts/tools needed.
        If service center is needed, explain what the technician will likely do.
        
        ## ADDITIONAL TIPS
        2-3 preventive tips to avoid this issue in the future.
        """

        load_dotenv(override=True)
        fresh_key = os.getenv("GOOGLE_API_KEY")
        if not fresh_key:
            raise ValueError("GOOGLE_API_KEY not found in environment. Please set it in your .env file.")
        client = genai.Client(api_key=fresh_key)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=diagnosis_prompt,
            config=genai_types.GenerateContentConfig(temperature=0.3)
        )
        full_text = response.text

        # Parse Sections
        sections = {
            "causes": "",
            "fixes": "",
            "verdict": "",
            "tips": "",
            "raw": full_text
        }

        lines = full_text.split("\n")
        current_section = None
        buffer = []

        for line in lines:
            line_upper = line.upper()
            if "## POSSIBLE CAUSES" in line_upper:
                current_section = "causes"
                buffer = []
            elif "## RECOMMENDED FIXES" in line_upper:
                if current_section:
                    sections[current_section] = "\n".join(buffer).strip()
                current_section = "fixes"
                buffer = []
            elif "## VERDICT" in line_upper:
                if current_section:
                    sections[current_section] = "\n".join(buffer).strip()
                current_section = "verdict"
                buffer = []
            elif "## ADDITIONAL TIPS" in line_upper:
                if current_section:
                    sections[current_section] = "\n".join(buffer).strip()
                current_section = "tips"
                buffer = []
            else:
                if current_section:
                    buffer.append(line)

        if current_section and buffer:
            sections[current_section] = "\n".join(buffer).strip()

        return sections

    # ── PATH B: Safe Intelligent Offline Fallback (API 503/429) ──
    except Exception as e:
        # Determine category based on user query
        query_lower = user_issue.lower()
        category = "general"
        
        if any(k in query_lower for k in ["battery", "charge", "power", "charger"]):
            category = "battery"
        elif any(k in query_lower for k in ["fan", "heat", "hot", "overheat", "temperature"]):
            category = "fan"
        elif any(k in query_lower for k in ["ssd", "storage", "boot", "drive"]):
            category = "ssd"
        elif any(k in query_lower for k in ["ram", "memory", "lag", "beep"]):
            category = "ram"
            
        fallback = FALLBACK_DIAGNOSES[category]
        
        # Format the parsed sections exactly as expected by the UI formatter
        fallback_sections = {
            "causes": fallback["causes"],
            "fixes": fallback["fixes"],
            "verdict": fallback["verdict"],
            "tips": fallback["tips"],
            "raw": f"Offline local fallback diagnosis due to API unavailability: {e}"
        }
        return fallback_sections

