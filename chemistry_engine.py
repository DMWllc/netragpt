import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from io import BytesIO
import base64
from matplotlib.patches import Circle, FancyBboxPatch, ConnectionPatch # type: ignore
import networkx as nx # type: ignore

class ChemistryEngine:
    def __init__(self):
        self.chemical_constants = {
            'R': 8.314,  # Gas constant J/(mol·K)
            'F': 96485,  # Faraday constant C/mol
            'Na': 6.022e23,  # Avogadro's number
            'h': 6.626e-34,  # Planck's constant
            'k': 1.381e-23,  # Boltzmann constant
        }
        
        # Common substituent effects
        self.substituent_effects = {
            'ortho_para_directors': ['-OH', '-NH2', '-OCH3', '-CH3', '-Cl', '-Br'],
            'meta_directors': ['-NO2', '-CN', '-SO3H', '-COOH', '-CHO', '-COR'],
            'activators': ['-OH', '-NH2', '-OCH3', '-CH3'],
            'deactivators': ['-NO2', '-CN', '-SO3H', '-COOH']
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
    
    def create_mechanism_diagram(self, mechanism_type, parameters=None):
        """Create chemical mechanism diagrams"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.set_facecolor('#0f0f23')
            fig.patch.set_facecolor('#0f0f23')
            
            if mechanism_type == 'friedel_crafts':
                return self._create_friedel_crafts_mechanism(ax, parameters, fig)
            elif mechanism_type == 'electrophilic_aromatic_substitution':
                return self._create_eas_mechanism(ax, parameters, fig)
            elif mechanism_type == 'substituent_effects':
                return self._create_substituent_effects_diagram(ax, parameters, fig)
            elif mechanism_type == 'synthesis_planning':
                return self._create_synthesis_planning_diagram(ax, parameters, fig)
                
        except Exception as e:
            print(f"Mechanism diagram error: {e}")
            return None
    
    def _create_benzene_ring(self, ax, center_x=0, center_y=0, size=1, color='white'):
        """Draw a benzene ring"""
        angles = np.linspace(0, 2*np.pi, 7)
        x = center_x + size * np.cos(angles)
        y = center_y + size * np.sin(angles)
        
        # Draw hexagon
        ax.plot(x, y, color=color, linewidth=2)
        
        # Draw circle inside for aromaticity
        circle = Circle((center_x, center_y), size*0.7, fill=False, 
                       color=color, linestyle='--', alpha=0.5)
        ax.add_patch(circle)
        
        return x, y
    
    def _create_friedel_crafts_mechanism(self, ax, parameters, fig):
        """Create Friedel-Crafts acylation/alkylation mechanism diagram"""
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2, 2)
        
        # Draw benzene ring
        self._create_benzene_ring(ax, center_x=-1, center_y=0, size=0.8)
        
        # Draw electrophile formation
        if parameters.get('reaction_type', 'acylation') == 'acylation':
            # Acyl chloride + AlCl3
            ax.text(-2.5, 1.5, 'R-C(=O)-Cl + AlCl₃', color='cyan', fontsize=10)
            ax.text(-2.5, 1.2, '→ R-C⁺=O + AlCl₄⁻', color='yellow', fontsize=10)
            
            # Draw acylium ion
            ax.text(1, 0.5, 'R-C⁺=O', color='red', fontsize=12, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
            
        else:  # alkylation
            # Alkyl halide + AlCl3
            ax.text(-2.5, 1.5, 'R-X + AlCl₃', color='cyan', fontsize=10)
            ax.text(-2.5, 1.2, '→ R⁺ + AlCl₄⁻', color='yellow', fontsize=10)
            
            # Draw carbocation
            ax.text(1, 0.5, 'R⁺', color='red', fontsize=12,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        # Draw reaction arrow
        ax.arrow(-0.2, 0, 0.4, 0, head_width=0.1, head_length=0.1, 
                fc='magenta', ec='magenta', linewidth=2)
        
        # Draw product benzene ring with substituent
        self._create_benzene_ring(ax, center_x=2, center_y=0, size=0.8)
        
        if parameters.get('reaction_type', 'acylation') == 'acylation':
            ax.text(2.2, 0.3, 'C=O-R', color='green', fontsize=10, rotation=45)
        else:
            ax.text(2.2, 0.3, 'R', color='green', fontsize=10)
        
        ax.set_title('Friedel-Crafts Reaction Mechanism', color='white', fontsize=16)
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)
    
    def _create_eas_mechanism(self, ax, parameters, fig):
        """Create Electrophilic Aromatic Substitution mechanism"""
        ax.set_xlim(-2, 8)
        ax.set_ylim(-2, 2)
        
        # Step 1: Electrophile attack
        self._create_benzene_ring(ax, center_x=1, center_y=0, size=0.7)
        ax.text(1.8, 0.5, 'E⁺', color='red', fontsize=12)
        ax.arrow(1.6, 0.4, -0.4, -0.3, head_width=0.1, head_length=0.1, 
                fc='red', ec='red')
        
        ax.text(1, -1.2, 'Step 1: Electrophile Attack', color='yellow', fontsize=10)
        
        # Step 2: Arenium ion formation
        self._create_benzene_ring(ax, center_x=3.5, center_y=0, size=0.7)
        ax.plot([3.5, 4.0], [0.7, 1.0], color='white', linewidth=2)  # Broken aromaticity
        ax.text(4.2, 0.8, 'E', color='green', fontsize=10)
        ax.text(4.2, 0.5, 'H', color='cyan', fontsize=10)
        
        ax.text(3.5, -1.2, 'Step 2: Arenium Ion', color='yellow', fontsize=10)
        
        # Step 3: Proton loss
        self._create_benzene_ring(ax, center_x=6, center_y=0, size=0.7)
        ax.text(6.8, 0.3, 'E', color='green', fontsize=10)
        ax.text(6.2, -0.8, 'H⁺', color='orange', fontsize=10)
        ax.arrow(6.5, -0.6, 0.3, 0.8, head_width=0.1, head_length=0.1, 
                fc='orange', ec='orange')
        
        ax.text(6, -1.2, 'Step 3: Proton Loss', color='yellow', fontsize=10)
        
        # Reaction arrows between steps
        ax.arrow(1.8, 0, 1.0, 0, head_width=0.1, head_length=0.1, 
                fc='white', ec='white', linestyle='--')
        ax.arrow(4.2, 0, 1.1, 0, head_width=0.1, head_length=0.1, 
                fc='white', ec='white', linestyle='--')
        
        ax.set_title('Electrophilic Aromatic Substitution Mechanism', color='white', fontsize=14)
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)
    
    def _create_substituent_effects_diagram(self, ax, parameters, fig):
        """Create diagram showing ortho/para vs meta directing effects"""
        ax.set_xlim(-1, 10)
        ax.set_ylim(-1, 6)
        
        # Ortho/Para directors
        ax.text(1, 5, 'Ortho/Para Directors', color='green', fontsize=12, 
               weight='bold', ha='center')
        
        ortho_para_examples = ['-OH', '-NH₂', '-OCH₃', '-CH₃', '-Cl', '-Br']
        for i, group in enumerate(ortho_para_examples):
            # Draw benzene with substituent
            self._create_benzene_ring(ax, center_x=1, center_y=3.5-i*0.6, size=0.3)
            ax.text(1.4, 3.5-i*0.6, group, color='cyan', fontsize=9)
            
            # Show attack positions
            if i == 0:  # Just for first example
                ax.text(1.8, 3.5, 'Attack here', color='yellow', fontsize=8)
                ax.scatter([1.15, 0.85, 1.0], [3.65, 3.35, 3.2], color='red', s=30)
        
        # Meta directors
        ax.text(5, 5, 'Meta Directors', color='red', fontsize=12, 
               weight='bold', ha='center')
        
        meta_examples = ['-NO₂', '-CN', '-SO₃H', '-COOH', '-CHO']
        for i, group in enumerate(meta_examples):
            # Draw benzene with substituent
            self._create_benzene_ring(ax, center_x=5, center_y=3.5-i*0.6, size=0.3)
            ax.text(5.4, 3.5-i*0.6, group, color='orange', fontsize=9)
            
            # Show attack positions
            if i == 0:  # Just for first example
                ax.text(5.8, 3.5, 'Attack here', color='yellow', fontsize=8)
                ax.scatter([4.7, 5.0, 5.3], [3.2, 3.2, 3.2], color='red', s=30)
        
        # Key points
        key_points = [
            "Ortho/Para: Electron Donating",
            "Meta: Electron Withdrawing", 
            "Order Matters in Synthesis!"
        ]
        
        for i, point in enumerate(key_points):
            ax.text(8, 4-i*0.8, point, color='white', fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='blue', alpha=0.3))
        
        ax.set_title('Aromatic Substituent Effects', color='white', fontsize=16)
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)
    
    def _create_synthesis_planning_diagram(self, ax, parameters, fig):
        """Create synthesis planning diagram showing order of operations"""
        ax.set_xlim(-1, 12)
        ax.set_ylim(-1, 8)
        
        title = "Synthesis Planning: Order of Operations Matters!"
        ax.text(5.5, 7.5, title, color='yellow', fontsize=14, 
               weight='bold', ha='center')
        
        # Example 1: Meta director first
        ax.text(2.5, 6.5, 'Path A: Meta Director First', color='cyan', fontsize=11, 
               weight='bold', ha='center')
        
        # Step 1: Install meta director
        self._create_benzene_ring(ax, center_x=1, center_y=5.5, size=0.4)
        ax.text(1.5, 5.5, '+ NO₂', color='orange', fontsize=9)
        ax.arrow(1.8, 5.5, 0.8, 0, head_width=0.1, head_length=0.1, fc='white', ec='white')
        
        # Step 2: Try to install ortho/para (fails)
        self._create_benzene_ring(ax, center_x=3.5, center_y=5.5, size=0.4)
        ax.text(3.9, 5.5, 'NO₂', color='orange', fontsize=9)
        ax.text(3.5, 5.0, '+ CH₃ (meta only!)', color='red', fontsize=8)
        ax.arrow(4.3, 5.5, 0.8, 0, head_width=0.1, head_length=0.1, fc='red', ec='red')
        
        # Step 3: Meta product
        self._create_benzene_ring(ax, center_x=6, center_y=5.5, size=0.4)
        ax.text(6.4, 5.7, 'CH₃', color='green', fontsize=8)
        ax.text(6.0, 5.2, 'NO₂', color='orange', fontsize=8)
        ax.text(6.5, 4.8, 'Meta Product', color='white', fontsize=9, 
               bbox=dict(boxstyle="round,pad=0.2", facecolor='red', alpha=0.5))
        
        # Example 2: Ortho/Para director first  
        ax.text(8.5, 6.5, 'Path B: Ortho/Para Director First', color='green', fontsize=11,
               weight='bold', ha='center')
        
        # Step 1: Install ortho/para director
        self._create_benzene_ring(ax, center_x=7, center_y=5.5, size=0.4)
        ax.text(7.5, 5.5, '+ CH₃', color='green', fontsize=9)
        ax.arrow(7.8, 5.5, 0.8, 0, head_width=0.1, head_length=0.1, fc='white', ec='white')
        
        # Step 2: Install second group (ortho/para)
        self._create_benzene_ring(ax, center_x=9.5, center_y=5.5, size=0.4)
        ax.text(9.9, 5.5, 'CH₃', color='green', fontsize=9)
        ax.text(9.5, 5.0, '+ NO₂ (ortho/para!)', color='cyan', fontsize=8)
        ax.arrow(10.3, 5.5, 0.8, 0, head_width=0.1, head_length=0.1, fc='white', ec='white')
        
        # Step 3: Ortho/Para products
        self._create_benzene_ring(ax, center_x=12, center_y=5.5, size=0.4)
        ax.text(12.4, 5.8, 'NO₂', color='orange', fontsize=8)  # ortho
        ax.text(11.8, 5.2, 'CH₃', color='green', fontsize=8)   # para
        ax.text(12.5, 4.8, 'Ortho/Para Products', color='white', fontsize=9,
               bbox=dict(boxstyle="round,pad=0.2", facecolor='green', alpha=0.5))
        
        # Key insight box
        insight_text = "Key Insight:\nInstall Ortho/Para directors FIRST,\nthen Meta directors for desired positioning"
        ax.text(5.5, 2.5, insight_text, color='yellow', fontsize=12,
               ha='center', va='center',
               bbox=dict(boxstyle="round,pad=0.5", facecolor='purple', alpha=0.7))
        
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)
    
    def calculate_reaction_parameters(self, parameters):
        """Calculate chemical reaction parameters"""
        try:
            calculation_type = parameters.get('type', 'yield')
            
            if calculation_type == 'yield':
                theoretical = parameters.get('theoretical_yield', 0)
                actual = parameters.get('actual_yield', 0)
                
                if theoretical > 0:
                    percent_yield = (actual / theoretical) * 100
                    return {'percent_yield': percent_yield}
            
            elif calculation_type == 'concentration':
                moles = parameters.get('moles', 0)
                volume = parameters.get('volume', 1)
                return {'concentration': moles / volume}
                
            elif calculation_type == 'rate_constant':
                # Arrhenius equation approximation
                A = parameters.get('pre_exponential', 1e13)
                Ea = parameters.get('activation_energy', 50000)  # J/mol
                T = parameters.get('temperature', 298)  # K
                R = 8.314
                
                k = A * np.exp(-Ea / (R * T))
                return {'rate_constant': k}
                
        except Exception as e:
            print(f"Reaction calculation error: {e}")
            return None
    
    def predict_substitution_pattern(self, existing_group, new_group):
        """Predict substitution pattern based on existing substituent"""
        if existing_group in self.substituent_effects['ortho_para_directors']:
            if new_group in self.substituent_effects['ortho_para_directors']:
                return "Ortho/Para mixture (both activating)"
            else:  # new group is meta director
                return "Ortho/Para positions (existing controls)"
        else:  # existing is meta director
            if new_group in self.substituent_effects['ortho_para_directors']:
                return "Meta position (existing controls)"
            else:
                return "Meta position (both deactivating)"
    
    def process_chemistry_query(self, message):
        """Process chemistry-related queries"""
        chemistry_content = {
            'visualizations': [],
            'calculations': [],
            'explanations': [],
            'predictions': []
        }
        
        message_lower = message.lower()
        
        # Mechanism detection
        mechanism_keywords = {
            'friedel crafts': 'friedel_crafts',
            'electrophilic aromatic substitution': 'electrophilic_aromatic_substitution', 
            'eas': 'electrophilic_aromatic_substitution',
            'substituent effect': 'substituent_effects',
            'ortho para meta': 'substituent_effects',
            'synthesis planning': 'synthesis_planning',
            'order of operations': 'synthesis_planning'
        }
        
        # Create visualizations
        for keyword, diagram_type in mechanism_keywords.items():
            if keyword in message_lower:
                params = {}
                if 'alkylation' in message_lower:
                    params['reaction_type'] = 'alkylation'
                elif 'acylation' in message_lower:
                    params['reaction_type'] = 'acylation'
                    
                visualization = self.create_mechanism_diagram(diagram_type, params)
                if visualization:
                    chemistry_content['visualizations'].append({
                        'type': diagram_type,
                        'image': visualization
                    })
        
        # Perform calculations
        if any(word in message_lower for word in ['calculate', 'yield', 'concentration']):
            if 'yield' in message_lower:
                calc_result = self.calculate_reaction_parameters({'type': 'yield'})
                if calc_result:
                    chemistry_content['calculations'].append(calc_result)
            
            if 'concentration' in message_lower:
                calc_result = self.calculate_reaction_parameters({'type': 'concentration'})
                if calc_result:
                    chemistry_content['calculations'].append(calc_result)
        
        # Make predictions
        if any(word in message_lower for word in ['predict', 'substitution', 'directing']):
            prediction = self.predict_substitution_pattern('-NO2', '-CH3')
            chemistry_content['predictions'].append({
                'prediction': prediction,
                'explanation': 'Based on substituent effects and directing properties'
            })
        
        # Add explanations
        if 'aromatic' in message_lower and 'synthesis' in message_lower:
            chemistry_content['explanations'].append(
                "In aromatic synthesis, install ortho/para directors FIRST, then meta directors. "
                "This controls the position of subsequent substitutions."
            )
        
        return chemistry_content

# Create global instance
chemistry_engine = ChemistryEngine()