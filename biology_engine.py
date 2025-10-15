import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from io import BytesIO
import base64
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Rectangle # type: ignore
import networkx as nx # type: ignore

class BiologyEngine:
    def __init__(self):
        self.biological_constants = {
            'avogadro': 6.022e23,
            'gas_constant': 8.314,
            'faraday_constant': 96485,
            'calorie_to_joule': 4.184
        }
        
        # Metabolic pathway data
        self.metabolic_pathways = {
            'krebs_cycle': {
                'compounds': {
                    'Acetyl-CoA': {'color': '#FF6B6B', 'type': 'substrate'},
                    'Citrate': {'color': '#4ECDC4', 'type': 'intermediate'},
                    'Isocitrate': {'color': '#45B7D1', 'type': 'intermediate'},
                    'α-Ketoglutarate': {'color': '#96CEB4', 'type': 'intermediate'},
                    'Succinyl-CoA': {'color': '#FFEAA7', 'type': 'intermediate'},
                    'Succinate': {'color': '#DDA0DD', 'type': 'intermediate'},
                    'Fumarate': {'color': '#98D8C8', 'type': 'intermediate'},
                    'Malate': {'color': '#F7DC6F', 'type': 'intermediate'},
                    'Oxaloacetate': {'color': '#BB8FCE', 'type': 'intermediate'}
                },
                'enzymes': {
                    'Citrate synthase': {'color': '#E74C3C'},
                    'Aconitase': {'color': '#3498DB'},
                    'Isocitrate dehydrogenase': {'color': '#2ECC71'},
                    'α-Ketoglutarate dehydrogenase': {'color': '#F39C12'},
                    'Succinyl-CoA synthetase': {'color': '#9B59B6'},
                    'Succinate dehydrogenase': {'color': '#1ABC9C'},
                    'Fumarase': {'color': '#D35400'},
                    'Malate dehydrogenase': {'color': '#34495E'}
                },
                'cofactors': {
                    'NAD+': {'color': '#E67E22'},
                    'NADH': {'color': '#27AE60'},
                    'FAD': {'color': '#8E44AD'},
                    'FADH2': {'color': '#16A085'},
                    'ATP': {'color': '#C0392B'},
                    'GTP': {'color': '#2980B9'},
                    'CO₂': {'color': '#7F8C8D'}
                }
            }
        }
    
    def save_plot_to_base64(self, fig):
        """Save matplotlib figure to base64 string"""
        try:
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                       facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close(fig)
            
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{image_base64}"
        except Exception as e:
            print(f"Plot saving error: {e}")
            return None
    
    def create_biochemical_diagram(self, diagram_type, parameters=None):
        """Create biochemical pathway diagrams"""
        try:
            fig, ax = plt.subplots(figsize=(14, 10))
            ax.set_facecolor('#0f0f23')
            fig.patch.set_facecolor('#0f0f23')
            
            if diagram_type == 'krebs_cycle':
                return self._create_krebs_cycle(ax, parameters, fig)
            elif diagram_type == 'glycolysis':
                return self._create_glycolysis_pathway(ax, parameters, fig)
            elif diagram_type == 'electron_transport_chain':
                return self._create_etc_diagram(ax, parameters, fig)
            elif diagram_type == 'dna_replication':
                return self._create_dna_replication(ax, parameters, fig)
            elif diagram_type == 'protein_synthesis':
                return self._create_protein_synthesis(ax, parameters, fig)
            elif diagram_type == 'cell_structure':
                return self._create_cell_diagram(ax, parameters, fig)
                
        except Exception as e:
            print(f"Biochemical diagram error: {e}")
            return None
    
    def _create_krebs_cycle(self, ax, parameters, fig):
        """Create detailed Krebs cycle diagram"""
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        
        # Title
        ax.text(6, 9.5, 'Krebs Cycle (Citric Acid Cycle)', 
               color='white', fontsize=16, weight='bold', ha='center')
        
        # Draw circular arrangement for Krebs cycle
        center_x, center_y = 6, 5
        radius = 3.5
        
        # Define positions for compounds in circular arrangement
        compounds = {
            'Acetyl-CoA': (center_x + radius * np.cos(0), center_y + radius * np.sin(0)),
            'Citrate': (center_x + radius * np.cos(np.pi/4), center_y + radius * np.sin(np.pi/4)),
            'Isocitrate': (center_x + radius * np.cos(np.pi/2), center_y + radius * np.sin(np.pi/2)),
            'α-Ketoglutarate': (center_x + radius * np.cos(3*np.pi/4), center_y + radius * np.sin(3*np.pi/4)),
            'Succinyl-CoA': (center_x + radius * np.cos(np.pi), center_y + radius * np.sin(np.pi)),
            'Succinate': (center_x + radius * np.cos(5*np.pi/4), center_y + radius * np.sin(5*np.pi/4)),
            'Fumarate': (center_x + radius * np.cos(3*np.pi/2), center_y + radius * np.sin(3*np.pi/2)),
            'Malate': (center_x + radius * np.cos(7*np.pi/4), center_y + radius * np.sin(7*np.pi/4)),
            'Oxaloacetate': (center_x + radius * np.cos(2*np.pi), center_y + radius * np.sin(2*np.pi))
        }
        
        # Draw connecting arrows (circular pathway)
        compound_list = list(compounds.keys())
        for i in range(len(compound_list)):
            current_compound = compound_list[i]
            next_compound = compound_list[(i + 1) % len(compound_list)]
            
            x1, y1 = compounds[current_compound]
            x2, y2 = compounds[next_compound]
            
            # Draw curved arrows for circular flow
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='cyan', lw=2, alpha=0.8))
        
        # Draw compound nodes
        for compound, (x, y) in compounds.items():
            color = self.metabolic_pathways['krebs_cycle']['compounds'][compound]['color']
            
            # Draw compound box
            box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                               boxstyle="round,pad=0.1", facecolor=color, alpha=0.8)
            ax.add_patch(box)
            ax.text(x, y, compound, ha='center', va='center', 
                   fontsize=8, weight='bold', color='black')
        
        # Add enzymes and reactions
        enzymes_info = {
            'Citrate synthase': (center_x + 1, center_y + 2),
            'Aconitase': (center_x + 3, center_y + 3),
            'Isocitrate dehydrogenase': (center_x + 3, center_y - 1),
            'α-Ketoglutarate dehydrogenase': (center_x - 1, center_y - 2),
            'Succinyl-CoA synthetase': (center_x - 3, center_y),
            'Succinate dehydrogenase': (center_x - 2, center_y + 3),
            'Fumarase': (center_x + 1, center_y - 3),
            'Malate dehydrogenase': (center_x + 4, center_y)
        }
        
        for enzyme, (x, y) in enzymes_info.items():
            color = self.metabolic_pathways['krebs_cycle']['enzymes'][enzyme]['color']
            ax.text(x, y, enzyme, ha='center', va='center', 
                   fontsize=7, color=color, style='italic',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.7))
        
        # Add energy products
        energy_products = {
            '3 NADH': (1, 8),
            '1 FADH₂': (1, 7.5),
            '1 GTP': (1, 7),
            '2 CO₂': (1, 6.5)
        }
        
        for product, (x, y) in energy_products.items():
            ax.text(x, y, product, ha='left', va='center', 
                   fontsize=10, color='yellow', weight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='green', alpha=0.5))
        
        # Add input substrates
        ax.text(10, 8, 'Inputs:', color='white', fontsize=12, weight='bold')
        ax.text(10, 7.5, 'Acetyl-CoA', color='#FF6B6B', fontsize=10)
        ax.text(10, 7, 'Oxaloacetate', color='#BB8FCE', fontsize=10)
        
        # Add cofactors
        cofactor_positions = {
            'NAD⁺ → NADH': (10, 3),
            'FAD → FADH₂': (10, 2.5),
            'GDP → GTP': (10, 2)
        }
        
        for cofactor, (x, y) in cofactor_positions.items():
            ax.text(x, y, cofactor, ha='left', va='center', 
                   fontsize=9, color='orange')
        
        # Add overall reaction
        reaction_text = "Overall: Acetyl-CoA + 3NAD⁺ + FAD + GDP + Pi + 2H₂O →\n2CO₂ + 3NADH + FADH₂ + GTP + 2H⁺ + CoA"
        ax.text(6, 0.5, reaction_text, ha='center', va='center',
               fontsize=9, color='cyan', style='italic',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='purple', alpha=0.3))
        
        ax.axis('off')
        return self.save_plot_to_base64(fig)
    
    def _create_glycolysis_pathway(self, ax, parameters, fig):
        """Create glycolysis pathway diagram"""
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        
        ax.text(6, 9.5, 'Glycolysis Pathway', color='white', fontsize=16, weight='bold', ha='center')
        
        # Glycolysis steps in linear arrangement
        steps = [
            ('Glucose', 1, 8, '#FF6B6B'),
            ('Glucose-6-P', 3, 8, '#4ECDC4'),
            ('Fructose-6-P', 5, 8, '#45B7D1'),
            ('Fructose-1,6-BP', 7, 8, '#96CEB4'),
            ('G3P + DHAP', 9, 8, '#FFEAA7'),
            ('1,3-BPG', 9, 6, '#DDA0DD'),
            ('3-PG', 7, 6, '#98D8C8'),
            ('2-PG', 5, 6, '#F7DC6F'),
            ('PEP', 3, 6, '#BB8FCE'),
            ('Pyruvate', 1, 6, '#E74C3C')
        ]
        
        # Draw steps and connections
        for i, (compound, x, y, color) in enumerate(steps):
            # Draw compound box
            box = FancyBboxPatch((x-0.7, y-0.25), 1.4, 0.5,
                               boxstyle="round,pad=0.1", facecolor=color, alpha=0.8)
            ax.add_patch(box)
            ax.text(x, y, compound, ha='center', va='center', 
                   fontsize=7, weight='bold', color='black')
            
            # Draw arrows between steps
            if i < len(steps) - 1:
                next_x, next_y = steps[i+1][1], steps[i+1][2]
                ax.annotate('', xy=(next_x-0.7, next_y), xytext=(x+0.7, y),
                           arrowprops=dict(arrowstyle='->', color='white', lw=1.5))
        
        # Add ATP/ADP changes
        atp_changes = [
            ('ATP → ADP', 2, 8.5, 'red'),
            ('ATP → ADP', 6, 8.5, 'red'),
            ('ADP → ATP', 8, 7, 'green'),
            ('ADP → ATP', 2, 5.5, 'green')
        ]
        
        for change, x, y, color in atp_changes:
            ax.text(x, y, change, ha='center', va='center',
                   fontsize=8, color=color, weight='bold')
        
        # Add NAD+ reduction
        ax.text(8, 5, 'NAD⁺ → NADH', ha='center', va='center',
               fontsize=8, color='orange', weight='bold')
        
        # Net ATP calculation
        ax.text(10, 7, 'Net ATP Gain: 2 ATP', ha='center', va='center',
               fontsize=12, color='yellow', weight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='blue', alpha=0.5))
        
        ax.axis('off')
        return self.save_plot_to_base64(fig)
    
    def _create_etc_diagram(self, ax, parameters, fig):
        """Create electron transport chain diagram"""
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        
        ax.text(6, 9.5, 'Electron Transport Chain & ATP Synthesis', 
               color='white', fontsize=16, weight='bold', ha='center')
        
        # Draw mitochondrial membrane
        ax.plot([2, 10], [7, 7], 'white', linewidth=3, label='Inner Mitochondrial Membrane')
        ax.text(6, 7.2, 'Inner Mitochondrial Membrane', ha='center', va='bottom',
               color='white', fontsize=10)
        
        # Protein complexes
        complexes = [
            ('Complex I\nNADH dehydrogenase', 3, 6, '#FF6B6B'),
            ('Complex II\nSuccinate dehydrogenase', 5, 6, '#4ECDC4'),
            ('Complex III\nCytochrome bc₁', 7, 6, '#45B7D1'),
            ('Complex IV\nCytochrome c oxidase', 9, 6, '#96CEB4')
        ]
        
        for name, x, y, color in complexes:
            rect = Rectangle((x-0.8, y-0.4), 1.6, 0.8, facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            ax.text(x, y, name, ha='center', va='center', fontsize=6, color='black')
        
        # Electron flow
        ax.annotate('', xy=(4, 6.5), xytext=(3, 6.5),
                   arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
        ax.annotate('', xy=(6, 6.5), xytext=(5, 6.5),
                   arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
        ax.annotate('', xy=(8, 6.5), xytext=(7, 6.5),
                   arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
        
        # Proton pumping
        for x in [3, 7, 9]:
            ax.annotate('', xy=(x, 7.5), xytext=(x, 7),
                       arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.text(x, 7.7, 'H⁺', ha='center', va='center', color='red', fontsize=8)
        
        # ATP synthase
        atp_synthase = FancyBboxPatch((4.5, 6.5), 1, 1.5, 
                                    boxstyle="round,pad=0.1", facecolor='purple', alpha=0.8)
        ax.add_patch(atp_synthase)
        ax.text(5, 7, 'ATP\nSynthase', ha='center', va='center', 
               fontsize=8, color='white', weight='bold')
        
        # Proton flow back through ATP synthase
        ax.annotate('', xy=(5, 7), xytext=(5, 7.5),
                   arrowprops=dict(arrowstyle='->', color='green', lw=2))
        
        # ATP production
        ax.text(5, 5.5, 'ADP + Pi → ATP', ha='center', va='center',
               fontsize=10, color='yellow', weight='bold')
        
        # Energy yield
        ax.text(10, 3, 'Energy Yield:\n~2.5 ATP/NADH\n~1.5 ATP/FADH₂', 
               ha='center', va='center', fontsize=10, color='cyan',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        ax.axis('off')
        return self.save_plot_to_base64(fig)
    
    def _create_dna_replication(self, ax, parameters, fig):
        """Create DNA replication diagram"""
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        
        ax.text(6, 9.5, 'DNA Replication Fork', color='white', fontsize=16, weight='bold', ha='center')
        
        # Parent DNA strand
        x_parent = np.linspace(2, 10, 50)
        y_parent = 7 + 0.1 * np.sin(x_parent * 2)
        ax.plot(x_parent, y_parent, 'cyan', linewidth=2, label='Parent Strand')
        
        # Complementary strand
        y_comp = 6 + 0.1 * np.sin(x_parent * 2 + np.pi)
        ax.plot(x_parent, y_comp, 'magenta', linewidth=2, label='Complementary Strand')
        
        # Base pairs
        for i in range(5, 45, 5):
            ax.plot([x_parent[i], x_parent[i]], [y_parent[i], y_comp[i]], 
                   'white', linewidth=1, alpha=0.6)
        
        # Replication fork
        ax.text(6, 7.5, 'Replication Fork →', ha='center', va='center', 
               color='yellow', fontsize=12, weight='bold')
        
        # Leading and lagging strands
        ax.text(4, 5, 'Leading Strand\n(Continuous)', ha='center', va='center',
               color='green', fontsize=10,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        ax.text(8, 5, 'Lagging Strand\n(Okazaki Fragments)', ha='center', va='center',
               color='orange', fontsize=10,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Enzymes
        enzymes = [
            ('DNA Polymerase', 5, 4, '#FF6B6B'),
            ('Helicase', 6, 8, '#4ECDC4'),
            ('Primase', 7, 4, '#45B7D1'),
            ('Ligase', 8, 3, '#96CEB4')
        ]
        
        for enzyme, x, y, color in enzymes:
            ax.text(x, y, enzyme, ha='center', va='center', fontsize=8, color=color,
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='black', alpha=0.5))
        
        ax.axis('off')
        return self.save_plot_to_base64(fig)
    
    def _create_cell_diagram(self, ax, parameters, fig):
        """Create eukaryotic cell structure diagram"""
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        
        ax.text(6, 9.5, 'Eukaryotic Cell Structure', color='white', fontsize=16, weight='bold', ha='center')
        
        # Cell membrane
        cell = Ellipse((6, 5), 8, 6, fill=False, color='white', linewidth=3)
        ax.add_patch(cell)
        ax.text(6, 1.5, 'Cell Membrane', ha='center', va='center', color='white', fontsize=10)
        
        # Nucleus
        nucleus = Ellipse((4, 5), 2, 1.5, facecolor='red', alpha=0.6)
        ax.add_patch(nucleus)
        ax.text(4, 5, 'Nucleus', ha='center', va='center', fontsize=9, weight='bold')
        
        # Mitochondria
        mitochondria = Ellipse((7, 6), 1, 0.7, facecolor='green', alpha=0.6)
        ax.add_patch(mitochondria)
        ax.text(7, 6, 'Mitochondria', ha='center', va='center', fontsize=8)
        
        # Endoplasmic reticulum
        x_er = 5 + 0.5 * np.sin(np.linspace(0, 2*np.pi, 50))
        y_er = 4 + 0.3 * np.cos(np.linspace(0, 2*np.pi, 50))
        ax.plot(x_er, y_er, 'orange', linewidth=2, alpha=0.7)
        ax.text(5, 3.5, 'ER', ha='center', va='center', color='orange', fontsize=8)
        
        # Golgi apparatus
        for i in range(3):
            golgi = Rectangle((8, 3.5 + i*0.3), 0.8, 0.2, facecolor='purple', alpha=0.6)
            ax.add_patch(golgi)
        ax.text(8.5, 4.5, 'Golgi', ha='center', va='center', color='purple', fontsize=8)
        
        # Ribosomes
        for i, (x, y) in enumerate([(5.5, 4.5), (6, 4.2), (5.8, 3.8)]):
            ribosome = Circle((x, y), 0.1, facecolor='yellow', alpha=0.8)
            ax.add_patch(ribosome)
        
        ax.text(6, 3, 'Ribosomes', ha='center', va='center', color='yellow', fontsize=8)
        
        ax.axis('off')
        return self.save_plot_to_base64(fig)
    
    def calculate_metabolic_yield(self, parameters):
        """Calculate metabolic energy yields"""
        try:
            pathway = parameters.get('pathway', 'glycolysis')
            
            if pathway == 'glycolysis':
                return {
                    'atp_produced': 4,
                    'atp_consumed': 2,
                    'net_atp': 2,
                    'nadh_produced': 2,
                    'pyruvate_produced': 2
                }
            elif pathway == 'krebs_cycle_per_acetyl_coa':
                return {
                    'nadh_produced': 3,
                    'fadh2_produced': 1,
                    'gtp_produced': 1,
                    'co2_produced': 2
                }
            elif pathway == 'complete_glucose_oxidation':
                return {
                    'total_atp': 30,
                    'glycolysis_atp': 2,
                    'krebs_cycle_atp': 2,
                    'etc_atp': 26
                }
                
        except Exception as e:
            print(f"Metabolic calculation error: {e}")
            return None
    
    def process_biology_query(self, message):
        """Process biology-related queries"""
        biology_content = {
            'visualizations': [],
            'calculations': [],
            'explanations': [],
            'pathways': []
        }
        
        message_lower = message.lower()
        
        # Biology diagram detection
        biology_keywords = {
            'krebs cycle': 'krebs_cycle',
            'citric acid cycle': 'krebs_cycle',
            'glycolysis': 'glycolysis',
            'electron transport chain': 'electron_transport_chain',
            'etc': 'electron_transport_chain',
            'dna replication': 'dna_replication',
            'protein synthesis': 'protein_synthesis',
            'cell structure': 'cell_structure',
            'eukaryotic cell': 'cell_structure'
        }
        
        # Create visualizations
        for keyword, diagram_type in biology_keywords.items():
            if keyword in message_lower:
                visualization = self.create_biochemical_diagram(diagram_type)
                if visualization:
                    biology_content['visualizations'].append({
                        'type': diagram_type,
                        'image': visualization
                    })
        
        # Perform calculations
        if any(word in message_lower for word in ['calculate', 'yield', 'atp']):
            if 'glycolysis' in message_lower:
                calc_result = self.calculate_metabolic_yield({'pathway': 'glycolysis'})
                if calc_result:
                    biology_content['calculations'].append(calc_result)
            
            if 'krebs' in message_lower:
                calc_result = self.calculate_metabolic_yield({'pathway': 'krebs_cycle_per_acetyl_coa'})
                if calc_result:
                    biology_content['calculations'].append(calc_result)
        
        # Add explanations
        if 'krebs' in message_lower:
            biology_content['explanations'].append(
                "The Krebs cycle completes the oxidation of glucose, producing high-energy "
                "electron carriers (NADH, FADH2) that drive ATP synthesis in the electron transport chain."
            )
        
        if 'glycolysis' in message_lower:
            biology_content['explanations'].append(
                "Glycolysis breaks down glucose into pyruvate, producing a net gain of 2 ATP "
                "and 2 NADH molecules through substrate-level phosphorylation."
            )
        
        return biology_content

# Create global instance
biology_engine = BiologyEngine()