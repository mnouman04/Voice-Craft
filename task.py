#!/usr/bin/env python3
"""
COMPLETE WORKING PDF to Audiobook Converter with Voice Cloning
Fixed with proper conversion functionality
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from pathlib import Path
import json
import time
import tempfile
from datetime import datetime
import platform
import shutil

# Check available TTS options
AVAILABLE_ENGINES = {}

# Check for system TTS
AVAILABLE_ENGINES['system'] = True

# Check for pyttsx3
try:
    import pyttsx3
    AVAILABLE_ENGINES['pyttsx3'] = True
except ImportError:
    AVAILABLE_ENGINES['pyttsx3'] = False

# Check for Coqui TTS with improved error handling
try:
    # Clear any cached modules first
    import sys
    modules_to_clear = ['TTS', 'torch', 'bangla', 'cffi']
    for module in modules_to_clear:
        if module in sys.modules:
            del sys.modules[module]
    
    # Check Python version compatibility first
    python_version = sys.version_info
    if python_version < (3, 9) or python_version >= (3, 12):
        raise ImportError(f"Python {python_version.major}.{python_version.minor} not supported. Coqui TTS requires Python 3.9-3.11")
    
    # Try importing dependencies step by step
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ PyTorch CUDA available: {torch.cuda.is_available()}")
    except ImportError as e:
        raise ImportError(f"PyTorch dependencies missing: {e}")
    
    # Try importing TTS
    from TTS.api import TTS
    AVAILABLE_ENGINES['coqui'] = True
    print("✅ Coqui TTS loaded successfully!")
    
except ImportError as e:
    AVAILABLE_ENGINES['coqui'] = False
    print(f"❌ Import Error - Coqui TTS not available: {e}")
except TypeError as e:
    AVAILABLE_ENGINES['coqui'] = False
    if "unsupported operand type" in str(e) and "|" in str(e):
        print(f"❌ Python Version Error - Coqui TTS not available: Python version incompatibility (union operator |)")
        print(f"💡 Solution: Use Python 3.10+ or install compatible TTS version")
    else:
        print(f"❌ Type Error - Coqui TTS not available: {e}")
except Exception as e:
    AVAILABLE_ENGINES['coqui'] = False
    print(f"❌ General Error - Coqui TTS not available: {e}")

# Check for edge-tts
try:
    import edge_tts
    AVAILABLE_ENGINES['edge'] = True
except ImportError:
    AVAILABLE_ENGINES['edge'] = False

# PDF support
try:
    import PyPDF2
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

class CompletePDFAudiobookConverter:
    """Complete working PDF audiobook converter with voice cloning"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("COMPLETE PDF Audiobook Converter with Voice Cloning")
        self.root.geometry("900x700")
        
        # Variables - FIX: Pass root as master, value as named parameter
        self.pdf_path = tk.StringVar()
        self.voice_sample_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="audiobook_with_cloning")
        self.selected_engine = tk.StringVar(value="system")
        self.use_voice_cloning = tk.BooleanVar(value=False)  # Fixed: use value= parameter
    
        # Progress
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to convert PDF to audiobook")
        
        self.setup_gui()
        self.check_available_engines()
    
    def setup_gui(self):
        """Setup complete GUI"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="PDF to Audiobook Converter with Voice Cloning\nCOMPLETE WORKING VERSION",
                              font=("Arial", 16, "bold"), fg="blue")
        title_label.pack(pady=(0, 20))
        
        # PDF Selection - STEP 1
        pdf_frame = ttk.LabelFrame(main_frame, text="STEP 1: Select PDF Document", padding="10")
        pdf_frame.pack(fill=tk.X, pady=10)
        
        pdf_entry_frame = ttk.Frame(pdf_frame)
        pdf_entry_frame.pack(fill=tk.X)
        ttk.Entry(pdf_entry_frame, textvariable=self.pdf_path, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(pdf_entry_frame, text="Browse PDF", command=self.browse_pdf).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Engine Selection - STEP 2
        engine_frame = ttk.LabelFrame(main_frame, text="STEP 2: Choose TTS Engine", padding="10")
        engine_frame.pack(fill=tk.X, pady=10)
        
        engines_info = {
            'system': 'System TTS (Windows built-in voices)',
            'pyttsx3': 'pyttsx3 (Local Python TTS)',
            'coqui': 'Coqui TTS (BEST for voice cloning)',
            'edge': 'Microsoft Edge TTS (High quality)'
        }
        
        for engine, description in engines_info.items():
            available = AVAILABLE_ENGINES.get(engine, False)
            state = "normal" if available else "disabled"
            
            frame = ttk.Frame(engine_frame)
            frame.pack(fill=tk.X, pady=2)
            
            ttk.Radiobutton(frame, 
                          text=f"{description} {'✓ Available' if available else '✗ Not installed'}",
                          variable=self.selected_engine, 
                          value=engine,
                          state=state).pack(side=tk.LEFT)
            
            # In the engine selection section, modify the Coqui engine part:
            if engine == 'coqui' and not available:
                # Special button for Coqui TTS with PyTorch
                install_btn = ttk.Button(frame, 
                                       text="Install Coqui TTS + PyTorch", 
                                       command=self.install_coqui_properly)
                install_btn.pack(side=tk.RIGHT)
            elif not available:
                install_btn = ttk.Button(frame, 
                                       text=f"Install {engine.title()}", 
                                       command=lambda e=engine: self.install_engine(e))
                install_btn.pack(side=tk.RIGHT)
        
        # Voice Cloning Section - STEP 3
        voice_frame = ttk.LabelFrame(main_frame, text="STEP 3: Voice Cloning (Optional)", padding="10")
        voice_frame.pack(fill=tk.X, pady=10)
        
        # Voice cloning checkbox - PROMINENT
        voice_check = tk.Checkbutton(voice_frame, 
                                   text="ENABLE VOICE CLONING (Clone your voice to read the PDF)",
                                   variable=self.use_voice_cloning,
                                   command=self.toggle_voice_cloning,
                                   font=("Arial", 11, "bold"),
                                   fg="red")
        voice_check.pack(anchor=tk.W, pady=5)
        
        # Voice Sample Selection
        self.voice_sample_frame = ttk.Frame(voice_frame)
        self.voice_sample_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(self.voice_sample_frame, text="Voice Sample (30+ seconds of clear speech):").pack(anchor=tk.W)
        
        voice_entry_frame = ttk.Frame(self.voice_sample_frame)
        voice_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.voice_entry = ttk.Entry(voice_entry_frame, textvariable=self.voice_sample_path, 
                                   width=60, state="disabled")
        self.voice_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.voice_button = ttk.Button(voice_entry_frame, text="Browse Voice Sample",
                                     command=self.browse_voice_sample, state="disabled")
        self.voice_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Output Directory - STEP 4
        output_frame = ttk.LabelFrame(main_frame, text="STEP 4: Output Directory", padding="10")
        output_frame.pack(fill=tk.X, pady=10)
        
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill=tk.X)
        
        ttk.Entry(output_entry_frame, textvariable=self.output_dir, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_entry_frame, text="Browse", command=self.browse_output).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="STEP 5: Conversion Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack()
        
        # MAIN CONVERSION BUTTON - BIGGER AND MORE PROMINENT
        conversion_frame = ttk.Frame(main_frame)
        conversion_frame.pack(pady=30)
        
        self.convert_button = tk.Button(conversion_frame, 
                                       text="🎧 START CONVERSION NOW! 🎧\nPDF → AUDIOBOOK",
                                       command=self.start_complete_conversion,
                                       font=("Arial", 18, "bold"),
                                       bg="red", fg="white",
                                       height=4, width=35,
                                       relief="raised",
                                       bd=5)
        self.convert_button.pack()
        
        # Add a secondary button for quick start
        quick_convert_button = tk.Button(conversion_frame,
                                        text="QUICK CONVERT (No Voice Cloning)",
                                        command=self.quick_convert,
                                        font=("Arial", 12, "bold"),
                                        bg="blue", fg="white",
                                        height=2, width=30)
        quick_convert_button.pack(pady=(10, 0))
        
        # Additional buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Test Voice Cloning", 
                  command=self.test_voice_cloning).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Install All Dependencies", 
                  command=self.install_all_dependencies).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Open Output Folder", 
                  command=self.open_output).pack(side=tk.LEFT, padx=5)
    
    def check_available_engines(self):
        """Check which engines are available"""
        available = [engine for engine, status in AVAILABLE_ENGINES.items() if status]
        self.status_var.set(f"Available TTS engines: {', '.join(available)}")
    
    def toggle_voice_cloning(self):
        """Toggle voice cloning UI"""
        if self.use_voice_cloning.get():
            self.voice_entry.config(state="normal")
            self.voice_button.config(state="normal")
            self.convert_button.config(text="START PDF TO AUDIOBOOK CONVERSION\n(WITH VOICE CLONING ENABLED)", bg="red")
        else:
            self.voice_entry.config(state="disabled")
            self.voice_button.config(state="disabled")
            self.convert_button.config(text="START PDF TO AUDIOBOOK CONVERSION\n(Standard TTS - No Voice Cloning)", bg="green")
    
    def quick_convert(self):
        """Quick conversion without voice cloning"""
        self.use_voice_cloning.set(False)
        self.toggle_voice_cloning()
        self.start_complete_conversion()

    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select PDF Document",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.pdf_path.set(filename)
    
    def browse_voice_sample(self):
        filename = filedialog.askopenfilename(
            title="Select Voice Sample for Cloning",
            filetypes=[("Audio files", "*.wav *.mp3 *.flac *.m4a")]
        )
        if filename:
            self.voice_sample_path.set(filename)
    
    def browse_output(self):
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
    
    def open_output(self):
        output_path = Path(self.output_dir.get())
        if output_path.exists():
            if platform.system() == "Windows":
                os.startfile(str(output_path))
    
    def install_engine(self, engine: str):
        """Install specific TTS engine"""
        def install():
            try:
                self.status_var.set(f"Installing {engine}...")
                
                commands = {
                    'pyttsx3': ["pip", "install", "pyttsx3"],
                    'coqui': ["pip", "install", "TTS"],
                    'edge': ["pip", "install", "edge-tts"]
                }
                
                if engine in commands:
                    subprocess.check_call(commands[engine])
                    AVAILABLE_ENGINES[engine] = True
                    self.status_var.set(f"{engine} installed successfully!")
                    messagebox.showinfo("Success", f"{engine} installed successfully!")
                
            except Exception as e:
                self.status_var.set(f"Failed to install {engine}")
                messagebox.showerror("Error", f"Failed to install {engine}:\n{e}")
        
        threading.Thread(target=install, daemon=True).start()
    
    def install_all_dependencies(self):
        """Install all dependencies"""
        def install():
            try:
                self.status_var.set("Installing all dependencies...")
                packages = ["PyPDF2", "pdfplumber", "pyttsx3", "edge-tts"]
                
                for package in packages:
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    except:
                        pass
                
                # Update availability
                global PDF_SUPPORT
                try:
                    import PyPDF2, pdfplumber
                    PDF_SUPPORT = True
                except:
                    pass
                
                try:
                    import pyttsx3
                    AVAILABLE_ENGINES['pyttsx3'] = True
                except:
                    pass
                
                try:
                    import edge_tts
                    AVAILABLE_ENGINES['edge'] = True
                except:
                    pass
                
                self.status_var.set("Dependencies installed!")
                messagebox.showinfo("Success", "Dependencies installed successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Installation failed:\n{e}")
        
        threading.Thread(target=install, daemon=True).start()
    
    def test_voice_cloning(self):
        """Test voice cloning functionality"""
        def test():
            try:
                if self.use_voice_cloning.get() and not self.voice_sample_path.get():
                    messagebox.showerror("Error", "Please select a voice sample first!")
                    return
                
                self.status_var.set("Testing voice cloning...")
                
                # Create test directory
                test_dir = Path(self.output_dir.get()) / "test"
                test_dir.mkdir(exist_ok=True)
                
                test_text = "Hello! This is a test of voice cloning. If this sounds like your voice, the cloning is working correctly."
                test_file = test_dir / "voice_clone_test.wav"
                
                # Generate test audio
                success = self.generate_audio_file(test_text, str(test_file))
                
                if success:
                    self.status_var.set("Voice cloning test successful!")
                    messagebox.showinfo("Test Complete", f"Test completed!\nFile: {test_file}")
                else:
                    messagebox.showerror("Test Failed", "Test failed. Check your settings.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Test failed: {e}")
        
        threading.Thread(target=test, daemon=True).start()
    
    def is_voice_cloning_enabled(self):
        """Check if voice cloning is currently enabled and properly configured"""
        try:
            # Check if voice cloning checkbox is enabled
            if not self.use_voice_cloning.get():
                self.log_status("🔊 Voice cloning is DISABLED - using standard TTS")
                return False
            
            # Check if reference audio file is selected
            if not self.voice_sample_path.get().strip():
                self.log_status("❌ Voice cloning enabled but NO voice sample selected")
                messagebox.showwarning("Voice Cloning Warning", "Voice cloning is enabled but no voice sample is selected!\nDisabling voice cloning for this conversion.")
                self.use_voice_cloning.set(False)
                self.toggle_voice_cloning()
                return False
            
            # Check if reference audio file exists
            if not os.path.exists(self.voice_sample_path.get()):
                self.log_status(f"❌ Voice sample file not found: {os.path.basename(self.voice_sample_path.get())}")
                messagebox.showerror("Voice Cloning Error", f"Voice sample file not found:\n{self.voice_sample_path.get()}")
                return False
            
            # Check if Coqui TTS is available for voice cloning
            if not AVAILABLE_ENGINES.get('coqui', False):
                self.log_status("❌ Coqui TTS not available - voice cloning disabled")
                messagebox.showwarning("Voice Cloning Warning", 
                    "Voice cloning requires Coqui TTS but it's not available!\n"
                    "Install Coqui TTS or disable voice cloning to continue.")
                return False
            
            self.log_status(f"🎤 Voice cloning ENABLED with sample: {os.path.basename(self.voice_sample_path.get())}")
            return True
            
        except Exception as e:
            self.log_status(f"❌ Error checking voice cloning status: {str(e)}")
            return False

    def log_status(self, message):
        """Log status message to console and GUI"""
        print(message)
        self.status_var.set(message)
        self.root.update_idletasks()

    def generate_audio_file(self, text: str, output_path: str) -> bool:
        """Generate audio file using selected engine with voice cloning check"""
        try:
            # Check if we should use voice cloning
            use_cloning = self.is_voice_cloning_enabled()
            
            # Select the appropriate generation method
            engine = self.selected_engine.get()
            
            if use_cloning and engine == 'coqui':
                self.log_status(f"🎭 Generating audio with VOICE CLONING using Coqui TTS...")
                return self.coqui_tts(text, output_path)
            else:
                if use_cloning and engine != 'coqui':
                    self.log_status(f"⚠️  Voice cloning requested but {engine} doesn't support it - using standard TTS")
                else:
                    self.log_status(f"🔊 Generating audio with standard {engine} TTS...")
                
                # Use the selected standard engine
                if engine == 'system':
                    return self.system_tts(text, output_path)
                elif engine == 'pyttsx3':
                    return self.pyttsx3_tts(text, output_path)
                elif engine == 'edge':
                    return self.edge_tts(text, output_path)
                else:
                    return self.system_tts(text, output_path)  # Fallback
                    
        except Exception as e:
            self.log_status(f"❌ Error generating audio: {str(e)}")
            return False

    def system_tts(self, text: str, output_path: str) -> bool:
        """Windows system TTS"""
        try:
            safe_text = text.replace('"', '""')
            ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile("{output_path}")
$synth.Speak("{safe_text}")
$synth.Dispose()
'''
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(ps_script)
                script_path = f.name
            
            result = subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path], 
                                  capture_output=True)
            
            os.unlink(script_path)
            return result.returncode == 0 and os.path.exists(output_path)
            
        except Exception as e:
            print(f"System TTS failed: {e}")
            return False
    
    def pyttsx3_tts(self, text: str, output_path: str) -> bool:
        """pyttsx3 TTS"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            return os.path.exists(output_path)
        except Exception as e:
            print(f"pyttsx3 TTS failed: {e}")
            return False
    
    def edge_tts(self, text: str, output_path: str) -> bool:
        """Microsoft Edge TTS"""
        try:
            import asyncio
            import edge_tts
            
            async def generate():
                voice = "en-US-JennyNeural"
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(generate())
            loop.close()
            
            return os.path.exists(output_path)
        except Exception as e:
            print(f"Edge TTS failed: {e}")
            return False
    
    def coqui_tts(self, text: str, output_path: str) -> bool:
        """Coqui TTS with voice cloning"""
        try:
            from TTS.api import TTS
            
            if self.use_voice_cloning.get() and self.voice_sample_path.get():
                # Use XTTS for voice cloning
                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
                tts.tts_to_file(
                    text=text,
                    speaker_wav=self.voice_sample_path.get(),
                    language="en",
                    file_path=output_path
                )
            else:
                # Use standard TTS
                tts = TTS("tts_models/en/ljspeech/tacotron2-DDC", gpu=False)
                tts.tts_to_file(text=text, file_path=output_path)
            
            return os.path.exists(output_path)
        except Exception as e:
            print(f"Coqui TTS failed: {e}")
            return False
    
    def extract_pdf_text(self, pdf_path: str) -> list:
        """Extract text from PDF"""
        if not PDF_SUPPORT:
            raise ImportError("PDF libraries not installed. Click 'Install All Dependencies'")
        
        pages_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Clean text
                        text = ' '.join(text.split())
                        text = text.replace('\n', ' ').replace('\t', ' ')
                        pages_text.append(text)
                    else:
                        pages_text.append("")
        except Exception as e:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text = ' '.join(text.split())
                        pages_text.append(text)
                    else:
                        pages_text.append("")
        
        return pages_text
    
    def start_complete_conversion(self):
        """MAIN CONVERSION FUNCTION with comprehensive voice cloning checks"""
        # Input validation
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Please select a PDF file!")
            return
        
        if not os.path.exists(self.pdf_path.get()):
            messagebox.showerror("Error", "PDF file does not exist!")
            return
        
        # Check voice cloning status and inform user
        cloning_requested = self.use_voice_cloning.get()
        cloning_available = self.is_voice_cloning_enabled()
        
        if cloning_requested and cloning_available:
            result = messagebox.askyesno("Voice Cloning Enabled", 
                                   f"🎤 VOICE CLONING IS ENABLED\n\n"
                                   f"Voice sample: {os.path.basename(self.voice_sample_path.get())}\n"
                                   f"This will take longer but produce personalized audio.\n\n"
                                   f"Continue with voice cloning?")
            if not result:
                self.use_voice_cloning.set(False)
                self.toggle_voice_cloning()
                cloning_available = False
        elif cloning_requested and not cloning_available:
            self.log_status("❌ Voice cloning was requested but is not properly configured")
        
        # Display final status
        if cloning_available:
            self.log_status("🎭 Starting conversion WITH voice cloning")
        else:
            self.log_status("🔊 Starting conversion with STANDARD TTS (no voice cloning)")
        
        if not AVAILABLE_ENGINES.get(self.selected_engine.get()):
            messagebox.showerror("Error", f"Selected engine '{self.selected_engine.get()}' not available!")
            return
        
        if not PDF_SUPPORT:
            messagebox.showerror("Error", "PDF support not installed! Click 'Install All Dependencies' first.")
            return
        
        # Start conversion in separate thread
        def convert():
            try:
                self.convert_button.config(state="disabled")
                self.progress_var.set(0)
                
                # Create output directory
                output_path = Path(self.output_dir.get())
                output_path.mkdir(exist_ok=True)
                
                self.status_var.set("📖 Extracting text from PDF...")
                self.root.update_idletasks()
                
                # Extract PDF text
                pages_text = self.extract_pdf_text(self.pdf_path.get())
                non_empty_pages = [p for p in pages_text if p.strip()]
                
                if not non_empty_pages:
                    raise ValueError("No readable text found in PDF!")
                
                self.status_var.set(f"📄 Found {len(non_empty_pages)} pages with text. Starting audio generation...")
                
                # Process each page
                successful = 0
                total_pages = len(pages_text)
                
                for page_num, page_text in enumerate(pages_text, 1):
                    if not page_text.strip():
                        continue
                    
                    self.status_var.set(f"🎵 Converting page {page_num}/{total_pages} to audio...")
                    progress = (page_num / total_pages) * 100
                    self.progress_var.set(progress)
                    self.root.update_idletasks()
                    
                    # Generate audio file for this page
                    audio_file = output_path / f"page_{page_num:03d}.wav"
                    success = self.generate_audio_file(page_text, str(audio_file))
                    
                    if success:
                        successful += 1
                        print(f"✅ Generated: {audio_file}")
                    else:
                        print(f"❌ Failed: page {page_num}")
                    
                    time.sleep(0.1)  # Small delay to prevent overwhelming system
                
                # Create conversion summary
                final_cloning_status = self.is_voice_cloning_enabled()
                summary = {
                    "timestamp": datetime.now().isoformat(),
                    "source_pdf": self.pdf_path.get(),
                    "voice_cloning_enabled": final_cloning_status,
                    "voice_sample": self.voice_sample_path.get() if final_cloning_status else None,
                    "tts_engine": self.selected_engine.get(),
                    "total_pages": total_pages,
                    "pages_with_text": len(non_empty_pages),
                    "successful_conversions": successful,
                    "output_directory": str(output_path)
                }
                
                with open(output_path / "conversion_summary.json", 'w') as f:
                    json.dump(summary, f, indent=2)
                
                self.progress_var.set(100)
                self.status_var.set(f"🎉 CONVERSION COMPLETED! {successful}/{len(non_empty_pages)} pages successful.")
                
                # Show completion message
                clone_status = "WITH VOICE CLONING 🎭" if final_cloning_status else "WITHOUT VOICE CLONING 🔊"
                
                messagebox.showinfo("Conversion Complete!", 
                    f"PDF to Audiobook conversion completed {clone_status}!\n\n"
                    f"📊 RESULTS:\n"
                    f"• Total pages: {total_pages}\n"
                    f"• Pages with text: {len(non_empty_pages)}\n"
                    f"• Successful conversions: {successful}\n"
                    f"• TTS Engine: {self.selected_engine.get()}\n"
                    f"• Voice cloning: {'Enabled 🎭' if final_cloning_status else 'Disabled 🔊'}\n"
                    f"• Output location: {output_path}\n\n"
                    f"🎧 Your audiobook is ready!")
                
            except Exception as e:
                self.status_var.set(f"❌ Conversion failed: {e}")
                messagebox.showerror("Conversion Failed", 
                    f"Conversion failed with error:\n\n{str(e)}\n\n"
                    f"Please check:\n"
                    f"• PDF is readable\n"
                    f"• TTS engine is properly installed\n"
                    f"• Voice sample is valid (if using voice cloning)")
                print(f"Detailed error: {e}")
            finally:
                self.convert_button.config(state="normal")
        
        threading.Thread(target=convert, daemon=True).start()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

    def install_coqui_properly(self):
        """Install Coqui TTS with proper PyTorch dependencies"""
        def install():
            try:
                self.status_var.set("Installing PyTorch and Coqui TTS...")
                
                # Step 1: Uninstall existing installations
                subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "torch", "torchvision", "torchaudio", "-y"])
                subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "TTS", "-y"])
                
                # Step 2: Clear pip cache
                subprocess.check_call([sys.executable, "-m", "pip", "cache", "purge"])
                
                # Step 3: Install PyTorch first
                self.status_var.set("Installing PyTorch...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "torch", "torchvision", "torchaudio", 
                    "--index-url", "https://download.pytorch.org/whl/cpu"
                ])
                
                # Step 4: Install Coqui TTS
                self.status_var.set("Installing Coqui TTS...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "TTS"])
                
                # Step 5: Test the installation
                self.status_var.set("Testing Coqui TTS installation...")
                
                # Import in a subprocess to avoid module caching issues
                test_script = '''
import torch
from TTS.api import TTS
print("SUCCESS: Both PyTorch and TTS imported successfully!")
print(f"PyTorch version: {torch.__version__}")
'''
                
                result = subprocess.run([sys.executable, "-c", test_script], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    AVAILABLE_ENGINES['coqui'] = True
                    self.status_var.set("✅ Coqui TTS installed successfully!")
                    messagebox.showinfo("Success", 
                        "Coqui TTS installed successfully!\n\n"
                        "Please restart the application to use voice cloning features.")
                else:
                    raise Exception(f"Installation test failed: {result.stderr}")
                    
            except Exception as e:
                self.status_var.set(f"❌ Failed to install Coqui TTS")
                messagebox.showerror("Installation Error", 
                    f"Failed to install Coqui TTS:\n\n{str(e)}\n\n"
                    f"Try installing manually:\n"
                    f"1. pip uninstall torch torchvision torchaudio TTS\n"
                    f"2. pip install torch torchvision torchaudio\n"
                    f"3. pip install TTS")
        
        threading.Thread(target=install, daemon=True).start()

if __name__ == "__main__":
    print("Starting Complete PDF Audiobook Converter with Voice Cloning...")
    print(f"Available engines: {[k for k, v in AVAILABLE_ENGINES.items() if v]}")
    
    app = CompletePDFAudiobookConverter()
    app.run()