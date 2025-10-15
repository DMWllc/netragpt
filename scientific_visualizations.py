import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, Polygon, FancyBboxPatch, Ellipse
import matplotlib.font_manager as fm
import networkx as nx
from matplotlib.patches import FancyArrowPatch, Arrow
import matplotlib.patches as mpatches
from matplotlib.path import Path
import io
import base64
import random

def save_plot_to_base64(fig):
    """Save matplotlib figure to base64 string"""
    try:
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                   facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Plot saving error: {e}")
        return None

def create_physics_visualization(physics_type, parameters=None):
    """Create physics diagrams and illustrations"""
    try:
        plt.rc('font', family='DejaVu Sans')
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_facecolor('#0f0f23')
        fig.patch.set_facecolor('#0f0f23')
        
        if physics_type == 'mechanics':
            return create_mechanics_diagram(ax, parameters, fig)
        elif physics_type == 'optics':
            return create_optics_diagram(ax, parameters, fig)
        elif physics_type == 'electricity':
            return create_electricity_diagram(ax, parameters, fig)
        elif physics_type == 'waves':
            return create_waves_diagram(ax, parameters, fig)
        elif physics_type == 'thermodynamics':
            return create_thermodynamics_diagram(ax, parameters)
        else:
            return create_general_physics_diagram(ax, parameters, fig)
            
    except Exception as e:
        print(f"Physics visualization error: {e}")
        return None

def create_mechanics_diagram(ax, parameters, fig=None):
    """Create mechanics diagrams (forces, motion, etc.)"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Draw an object (rectangle)
        rect = Rectangle((4, 4), 2, 2, fill=True, color='cyan', alpha=0.7)
        ax.add_patch(rect)
        
        # Draw force arrows
        # Gravity
        ax.arrow(5, 4, 0, -1, head_width=0.2, head_length=0.2, fc='red', ec='red', linewidth=2)
        ax.text(5.2, 3, 'Fg', color='red', fontsize=12)
        
        # Normal force
        ax.arrow(5, 6, 0, 1, head_width=0.2, head_length=0.2, fc='blue', ec='blue', linewidth=2)
        ax.text(5.2, 6.5, 'Fn', color='blue', fontsize=12)
        
        # Applied force
        ax.arrow(4, 5, -1, 0, head_width=0.2, head_length=0.2, fc='green', ec='green', linewidth=2)
        ax.text(2.5, 5.2, 'Fa', color='green', fontsize=12)
        
        # Friction
        ax.arrow(6, 5, 1, 0, head_width=0.2, head_length=0.2, fc='orange', ec='orange', linewidth=2)
        ax.text(6.5, 5.2, 'Ff', color='orange', fontsize=12)
        
        ax.set_title('Force Diagram - Mechanics', color='white', fontsize=14)
        ax.set_xlabel('Position', color='white')
        ax.set_ylabel('Force', color='white')
        ax.tick_params(colors='white')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Mechanics diagram error: {e}")
        return None

def create_optics_diagram(ax, parameters, fig=None):
    """Create optics diagrams (lens, reflection, refraction)"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Draw a convex lens
        lens_curve = np.linspace(3, 7, 100)
        lens_top = 5 + 0.5 * np.sin(np.pi * (lens_curve - 3) / 4)
        lens_bottom = 5 - 0.5 * np.sin(np.pi * (lens_curve - 3) / 4)
        
        ax.plot(lens_curve, lens_top, color='cyan', linewidth=3)
        ax.plot(lens_curve, lens_bottom, color='cyan', linewidth=3)
        
        # Draw light rays
        # Incident ray
        ax.plot([1, 4], [7, 5.5], color='yellow', linewidth=2)
        # Refracted ray
        ax.plot([4, 9], [5.5, 3], color='yellow', linewidth=2, linestyle='--')
        
        ax.set_title('Convex Lens - Optics', color='white', fontsize=14)
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Optics diagram error: {e}")
        return None

def create_electricity_diagram(ax, parameters, fig=None):
    """Create electricity and circuit diagrams"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Draw a simple circuit
        # Battery
        ax.add_patch(Rectangle((2, 6), 0.5, 2, fill=True, color='red'))
        ax.add_patch(Rectangle((2, 4), 0.5, 2, fill=True, color='black'))
        ax.text(2.7, 7, '+', color='white', fontsize=12)
        ax.text(2.7, 5, '-', color='white', fontsize=12)
        
        # Resistor
        ax.plot([4, 5, 5.5, 6, 6.5, 7, 7.5, 8], [7, 7, 6.5, 7, 6.5, 7, 6.5, 7], color='orange', linewidth=3)
        
        # Wires
        ax.plot([2.5, 4], [7, 7], color='yellow', linewidth=2)
        ax.plot([8, 9], [7, 7], color='yellow', linewidth=2)
        ax.plot([9, 2.5], [7, 5], color='yellow', linewidth=2)
        
        ax.set_title('Simple Electrical Circuit', color='white', fontsize=14)
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Electricity diagram error: {e}")
        return None

def create_waves_diagram(ax, parameters, fig=None):
    """Create wave diagrams"""
    try:
        x = np.linspace(0, 4*np.pi, 1000)
        y1 = np.sin(x)
        y2 = np.sin(2*x)
        
        ax.plot(x, y1, color='cyan', linewidth=2, label='Wave 1')
        ax.plot(x, y2, color='magenta', linewidth=2, label='Wave 2', linestyle='--')
        
        ax.set_title('Wave Interference', color='white', fontsize=14)
        ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
        ax.set_facecolor('#0f0f23')
        ax.tick_params(colors='white')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Waves diagram error: {e}")
        return None

def create_thermodynamics_diagram(ax, parameters):
    """Create thermodynamics diagrams"""
    try:
        # PV diagram example
        V = np.linspace(1, 10, 100)
        P_isothermal = 10/V
        P_adiabatic = 10/V**1.4
        
        ax.plot(V, P_isothermal, color='cyan', linewidth=2, label='Isothermal')
        ax.plot(V, P_adiabatic, color='magenta', linewidth=2, label='Adiabatic')
        
        ax.set_title('Thermodynamics: PV Diagram', color='white', fontsize=14)
        ax.set_xlabel('Volume (V)', color='white')
        ax.set_ylabel('Pressure (P)', color='white')
        ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
        ax.tick_params(colors='white')
        
        return save_plot_to_base64(plt.gcf())
        
    except Exception as e:
        print(f"Thermodynamics diagram error: {e}")
        return None

def create_general_physics_diagram(ax, parameters, fig=None):
    """Create general physics diagram"""
    try:
        # Simple coordinate system with vectors
        ax.axhline(y=5, color='white', linewidth=0.5)
        ax.axvline(x=5, color='white', linewidth=0.5)
        
        # Draw some vectors
        ax.arrow(5, 5, 2, 1, head_width=0.2, head_length=0.2, fc='cyan', ec='cyan')
        ax.arrow(5, 5, -1, 2, head_width=0.2, head_length=0.2, fc='magenta', ec='magenta')
        ax.arrow(5, 5, 1, -1, head_width=0.2, head_length=0.2, fc='yellow', ec='yellow')
        
        ax.text(7, 6.5, 'Vector A', color='cyan', fontsize=10)
        ax.text(3.5, 7, 'Vector B', color='magenta', fontsize=10)
        ax.text(6, 3.5, 'Vector C', color='yellow', fontsize=10)
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
    except Exception as e:
        print(f"General physics diagram error: {e}")
        return None

def create_biology_visualization(biology_type, parameters=None):
    """Create biology diagrams and illustrations"""
    try:
        plt.rc('font', family='DejaVu Sans')
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_facecolor('#0f0f23')
        fig.patch.set_facecolor('#0f0f23')
        
        if biology_type == 'cell':
            return create_cell_diagram(ax, parameters, fig)
        elif biology_type == 'dna':
            return create_dna_diagram(ax, parameters, fig)
        elif biology_type == 'krebs_cycle':
            return create_krebs_cycle_diagram(ax, parameters, fig)
        elif biology_type == 'ecosystem':
            return create_ecosystem_diagram(ax, parameters, fig)
        elif biology_type == 'neuron':
            return create_neuron_diagram(ax, parameters, fig)
        else:
            return create_general_biology_diagram(ax, parameters, fig)
            
    except Exception as e:
        print(f"Biology visualization error: {e}")
        return None

def create_cell_diagram(ax, parameters, fig=None):
    """Create cell structure diagram"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Cell membrane
        cell = Circle((5, 5), 3, fill=False, color='cyan', linewidth=3)
        ax.add_patch(cell)
        
        # Nucleus
        nucleus = Circle((5, 5), 1, fill=True, color='magenta', alpha=0.7)
        ax.add_patch(nucleus)
        
        # Mitochondria
        mitochondria = Ellipse((3, 6), 0.8, 0.4, angle=45, fill=True, color='yellow', alpha=0.7)
        ax.add_patch(mitochondria)
        
        # Ribosomes (dots)
        for i in range(8):
            x = 4 + random.random() * 2
            y = 3 + random.random() * 4
            ribosome = Circle((x, y), 0.1, fill=True, color='green')
            ax.add_patch(ribosome)
        
        ax.text(5, 8.5, 'Cell Membrane', color='cyan', fontsize=12, ha='center')
        ax.text(5, 5, 'Nucleus', color='white', fontsize=10, ha='center')
        ax.text(3, 6.5, 'Mitochondria', color='yellow', fontsize=8)
        
        ax.set_title('Animal Cell Structure', color='white', fontsize=16)
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Cell diagram error: {e}")
        return None

def create_dna_diagram(ax, parameters, fig=None):
    """Create DNA double helix diagram"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Draw DNA double helix (simplified)
        x = np.linspace(1, 9, 100)
        y1 = 5 + 2 * np.sin(2 * np.pi * x / 3)
        y2 = 5 + 2 * np.cos(2 * np.pi * x / 3)
        
        ax.plot(x, y1, color='cyan', linewidth=2, label='Strand 1')
        ax.plot(x, y2, color='magenta', linewidth=2, label='Strand 2')
        
        # Draw base pairs
        for i in range(0, 100, 10):
            ax.plot([x[i], x[i]], [y1[i], y2[i]], color='yellow', linewidth=1, alpha=0.7)
        
        ax.set_title('DNA Double Helix Structure', color='white', fontsize=16)
        ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"DNA diagram error: {e}")
        return None

def create_krebs_cycle_diagram(ax, parameters, fig=None):
    """Create Krebs Cycle (Citric Acid Cycle) diagram"""
    try:
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 12)
        
        # Create circular arrangement for Krebs cycle
        center_x, center_y = 6, 6
        radius = 4
        steps = 8
        
        # Draw cycle circle
        cycle_circle = Circle((center_x, center_y), radius, fill=False, color='cyan', linewidth=2, alpha=0.5)
        ax.add_patch(cycle_circle)
        
        # Metabolic intermediates
        intermediates = [
            "Acetyl-CoA", "Citrate", "Isocitrate", "α-Ketoglutarate",
            "Succinyl-CoA", "Succinate", "Fumarate", "Malate", "Oxaloacetate"
        ]
        
        # Draw intermediates as nodes
        for i, intermediate in enumerate(intermediates):
            angle = 2 * np.pi * i / len(intermediates)
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            
            # Draw node
            node = Circle((x, y), 0.3, fill=True, color='lightblue', alpha=0.8)
            ax.add_patch(node)
            
            # Add label
            ax.text(x, y - 0.5, intermediate, color='white', fontsize=8, 
                   ha='center', va='center', rotation=angle*180/np.pi)
        
        # Draw arrows between nodes (simplified)
        for i in range(len(intermediates)):
            angle1 = 2 * np.pi * i / len(intermediates)
            angle2 = 2 * np.pi * (i + 1) / len(intermediates)
            
            x1 = center_x + radius * np.cos(angle1)
            y1 = center_y + radius * np.sin(angle1)
            x2 = center_x + radius * np.cos(angle2)
            y2 = center_y + radius * np.sin(angle2)
            
            # Draw arrow
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='yellow', lw=1.5))
        
        # Add energy products
        ax.text(2, 2, 'ATP\nNADH\nFADH₂\nCO₂', color='lightgreen', fontsize=10,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='darkgreen', alpha=0.7))
        
        ax.set_title('Krebs Cycle (Citric Acid Cycle)', color='white', fontsize=16)
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Krebs cycle diagram error: {e}")
        return None

def create_ecosystem_diagram(ax, parameters, fig=None):
    """Create ecosystem diagram"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Sun
        sun = Circle((1, 9), 0.5, fill=True, color='yellow')
        ax.add_patch(sun)
        ax.text(1, 8, 'Sun', color='yellow', fontsize=10, ha='center')
        
        # Producers (plants)
        for i in range(3):
            x = 3 + i * 2
            plant = Rectangle((x-0.2, 7), 0.4, 1, fill=True, color='green')
            ax.add_patch(plant)
        
        # Primary consumers
        for i in range(2):
            x = 4 + i * 2
            consumer = Circle((x, 5), 0.3, fill=True, color='orange')
            ax.add_patch(consumer)
        
        # Secondary consumers
        predator = Circle((5, 3), 0.4, fill=True, color='red')
        ax.add_patch(predator)
        
        # Decomposers
        for i in range(4):
            x = 2 + i * 2
            decomposer = Circle((x, 1), 0.1, fill=True, color='brown')
            ax.add_patch(decomposer)
        
        # Energy flow arrows
        ax.annotate('', xy=(3, 7), xytext=(1.5, 8.5),
                   arrowprops=dict(arrowstyle='->', color='white', lw=1))
        ax.annotate('', xy=(4, 5.3), xytext=(3, 7),
                   arrowprops=dict(arrowstyle='->', color='white', lw=1))
        ax.annotate('', xy=(5, 3.4), xytext=(4, 5),
                   arrowprops=dict(arrowstyle='->', color='white', lw=1))
        ax.annotate('', xy=(2, 1.1), xytext=(5, 3),
                   arrowprops=dict(arrowstyle='->', color='white', lw=1))
        
        ax.text(3, 7.5, 'Producers', color='green', fontsize=9)
        ax.text(4, 5.5, 'Consumers', color='orange', fontsize=9)
        ax.text(5, 3.5, 'Predators', color='red', fontsize=9)
        ax.text(3, 1.5, 'Decomposers', color='brown', fontsize=9)
        
        ax.set_title('Ecosystem Energy Flow', color='white', fontsize=16)
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Ecosystem diagram error: {e}")
        return None

def create_neuron_diagram(ax, parameters, fig=None):
    """Create neuron diagram"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Cell body
        cell_body = Circle((3, 5), 1, fill=True, color='cyan', alpha=0.7)
        ax.add_patch(cell_body)
        
        # Dendrites
        for i in range(5):
            angle = np.pi/6 * (i - 2)
            x_end = 3 + 2 * np.cos(angle)
            y_end = 5 + 2 * np.sin(angle)
            ax.plot([3, x_end], [5, y_end], color='green', linewidth=2)
        
        # Axon
        ax.plot([4, 8], [5, 5], color='yellow', linewidth=3)
        
        # Axon terminals
        for i in range(3):
            y_terminal = 4 + i * 0.5
            ax.plot([8, 9], [5, y_terminal], color='magenta', linewidth=2)
        
        ax.text(3, 5, 'Cell Body', color='white', fontsize=10, ha='center')
        ax.text(2, 7, 'Dendrites', color='green', fontsize=9)
        ax.text(6, 4, 'Axon', color='yellow', fontsize=9)
        ax.text(8.5, 3, 'Terminals', color='magenta', fontsize=9)
        
        ax.set_title('Neuron Structure', color='white', fontsize=16)
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"Neuron diagram error: {e}")
        return None

def create_general_biology_diagram(ax, parameters, fig=None):
    """Create general biology diagram"""
    try:
        # Simple biological hierarchy
        levels = ['Biosphere', 'Ecosystem', 'Community', 'Population', 'Organism', 'Organ System', 'Organ', 'Tissue', 'Cell', 'Molecule']
        y_pos = np.linspace(1, 9, len(levels))
        
        for i, level in enumerate(levels):
            ax.text(5, y_pos[i], level, color='cyan', fontsize=12, ha='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='darkblue', alpha=0.7))
            if i < len(levels) - 1:
                ax.annotate(
                    '', 
                    xy=(5, y_pos[i] - 0.3), 
                    xytext=(5, y_pos[i+1] + 0.3),
                    arrowprops=dict(arrowstyle='->', color='white', lw=1)
                )

        ax.set_title('Biological Organization Levels', color='white', fontsize=16)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        if fig is not None:
            return save_plot_to_base64(fig)
        else:
            return None
        
    except Exception as e:
        print(f"General biology diagram error: {e}")
        return None

def create_chemical_mechanism_visualization(mechanism_type, parameters=None):
    """Create chemical reaction mechanisms with arrow pushing"""
    try:
        plt.rc('font', family='DejaVu Sans')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_facecolor('#0f0f23')
        fig.patch.set_facecolor('#0f0f23')
        
        if mechanism_type == 'alkene_hydration':
            return create_alkene_hydration_mechanism(ax, parameters)
        elif mechanism_type == 'sn2':
            return create_sn2_mechanism(ax, parameters)
        elif mechanism_type == 'electrophilic_aromatic':
            return create_electrophilic_aromatic_mechanism(ax, parameters)
        elif mechanism_type == 'carbonyl':
            return create_carbonyl_mechanism(ax, parameters)
        else:
            return create_general_mechanism(ax, parameters)
            
    except Exception as e:
        print(f"Chemical mechanism visualization error: {e}")
        return None

def create_alkene_hydration_mechanism(ax, parameters):
    """Create alkene to alcohol hydration mechanism"""
    try:
        ax.set_xlim(0, 15)
        ax.set_ylim(0, 10)
        
        # Step 1: Protonation of alkene
        ax.text(2, 8, 'Step 1: Protonation', color='yellow', fontsize=12, ha='center')
        
        # Alkene
        ax.text(2, 7, 'H₂C=CH₂', color='cyan', fontsize=14, ha='center')
        ax.text(1.5, 6.5, 'Alkene', color='white', fontsize=10, ha='center')
        
        # Arrow to carbocation
        ax.annotate('', xy=(4, 7), xytext=(2.5, 7),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        
        # Carbocation intermediate
        ax.text(5, 7, 'H₃C-CH₂⁺', color='magenta', fontsize=14, ha='center')
        ax.text(5, 6.5, 'Carbocation', color='white', fontsize=10, ha='center')
        
        # Step 2: Nucleophilic attack by water
        ax.text(8, 8, 'Step 2: Water Attack', color='yellow', fontsize=12, ha='center')
        
        # Arrow from carbocation to alcohol
        ax.annotate('', xy=(10, 7), xytext=(6, 7),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        
        # Alcohol product
        ax.text(11, 7, 'H₃C-CH₂-OH', color='lightgreen', fontsize=14, ha='center')
        ax.text(11, 6.5, 'Alcohol', color='white', fontsize=10, ha='center')
        
        # Add curved arrows for electron movement
        # Protonation arrow (curved)
        ax.annotate('', xy=(2.2, 6.8), xytext=(1.5, 6.2),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2, 
                                 connectionstyle="arc3,rad=0.3"))
        ax.text(1, 6, 'H⁺', color='red', fontsize=12)
        
        # Water attack arrow (curved)
        ax.annotate('', xy=(5.8, 6.8), xytext=(7, 6.2),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=2,
                                 connectionstyle="arc3,rad=0.3"))
        ax.text(7.5, 6, 'H₂O', color='blue', fontsize=12)
        
        # Add reaction conditions
        ax.text(6, 5, 'Reaction: H₂SO₄, H₂O\nMarkovnikov Addition', 
               color='orange', fontsize=10, ha='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='darkred', alpha=0.7))
        
        ax.set_title('Alkene Hydration Mechanism', color='white', fontsize=16)
        ax.axis('off')
        
        return save_plot_to_base64(plt.gcf())
        
    except Exception as e:
        print(f"Alkene hydration mechanism error: {e}")
        return None

def create_sn2_mechanism(ax, parameters):
    """Create SN2 reaction mechanism"""
    try:
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        
        # Reactants
        ax.text(2, 6, 'CH₃-Br + OH⁻', color='cyan', fontsize=14, ha='center')
        ax.text(2, 5.5, 'Reactants', color='white', fontsize=10, ha='center')
        
        # Transition state
        ax.text(6, 6, '[HO---CH₃---Br]⁻', color='magenta', fontsize=12, ha='center')
        ax.text(6, 5.5, 'Transition State', color='white', fontsize=10, ha='center')
        
        # Products
        ax.text(10, 6, 'HO-CH₃ + Br⁻', color='lightgreen', fontsize=14, ha='center')
        ax.text(10, 5.5, 'Products', color='white', fontsize=10, ha='center')
        
        # Arrows
        ax.annotate('', xy=(4, 6), xytext=(2.5, 6),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        ax.annotate('', xy=(8, 6), xytext=(7.5, 6),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        
        # Backside attack illustration
        ax.text(6, 3, 'Backside Attack', color='yellow', fontsize=12, ha='center')
        ax.plot([4, 8], [3, 3], 'w--', alpha=0.5)
        ax.annotate('', xy=(6, 3), xytext=(4, 3),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        ax.annotate('', xy=(6, 3), xytext=(8, 3),
                   arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        ax.text(4, 2.7, 'OH⁻', color='blue', fontsize=10)
        ax.text(8, 2.7, 'Br⁻', color='red', fontsize=10)
        
        ax.set_title('SN2 Reaction Mechanism', color='white', fontsize=16)
        ax.axis('off')
        
        return save_plot_to_base64(plt.gcf())
        
    except Exception as e:
        print(f"SN2 mechanism error: {e}")
        return None

def create_electrophilic_aromatic_mechanism(ax, parameters):
    """Create electrophilic aromatic substitution mechanism"""
    try:
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        
        # Step 1: Electrophile generation
        ax.text(2, 7, 'Step 1: Electrophile Formation', color='yellow', fontsize=10, ha='center')
        ax.text(2, 6, 'HNO₃ + H₂SO₄ → NO₂⁺', color='cyan', fontsize=12, ha='center')
        
        # Step 2: Attack on aromatic ring
        ax.text(6, 7, 'Step 2: Electrophilic Attack', color='yellow', fontsize=10, ha='center')
        ax.text(6, 6, 'C₆H₆ + NO₂⁺ → C₆H₆-NO₂⁺', color='magenta', fontsize=12, ha='center')
        
        # Step 3: Deprotonation
        ax.text(10, 7, 'Step 3: Deprotonation', color='yellow', fontsize=10, ha='center')
        ax.text(10, 6, 'C₆H₆-NO₂⁺ → C₆H₅-NO₂ + H⁺', color='lightgreen', fontsize=12, ha='center')
        
        # Arrows
        ax.annotate('', xy=(4, 6), xytext=(2.5, 6),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        ax.annotate('', xy=(8, 6), xytext=(7.5, 6),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        
        # Aromatic ring illustration
        ax.text(6, 4, 'Benzene Ring', color='orange', fontsize=10, ha='center',
               bbox=dict(boxstyle="circle,pad=0.3", facecolor='darkblue', alpha=0.7))
        
        ax.set_title('Electrophilic Aromatic Substitution', color='white', fontsize=14)
        ax.axis('off')
        
        return save_plot_to_base64(plt.gcf())
        
    except Exception as e:
        print(f"Electrophilic aromatic mechanism error: {e}")
        return None

def create_carbonyl_mechanism(ax, parameters):
    """Create carbonyl reaction mechanism"""
    try:
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        
        # Nucleophilic addition to carbonyl
        ax.text(2, 7, 'Carbonyl Compound', color='cyan', fontsize=12, ha='center')
        ax.text(2, 6.5, 'R-C=O', color='cyan', fontsize=14, ha='center')
        
        # Nucleophile attack
        ax.text(6, 7, 'Tetrahedral Intermediate', color='magenta', fontsize=10, ha='center')
        ax.text(6, 6.5, 'R-C-OH', color='magenta', fontsize=12, ha='center')
        ax.text(6, 6, '    Nu', color='magenta', fontsize=10)
        
        # Product
        ax.text(10, 7, 'Alcohol Product', color='lightgreen', fontsize=12, ha='center')
        ax.text(10, 6.5, 'R-CH-OH', color='lightgreen', fontsize=14, ha='center')
        ax.text(10, 6, '    Nu', color='lightgreen', fontsize=10)
        
        # Arrows with curved electron movement
        ax.annotate('', xy=(4, 6.5), xytext=(2.5, 6.5),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        
        ax.annotate('', xy=(8, 6.5), xytext=(7.5, 6.5),
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
        
        # Curved arrow for nucleophile attack
        ax.annotate('', xy=(3, 6), xytext=(5, 5),
                   arrowprops=dict(arrowstyle='->', color='blue', lw=2,
                                 connectionstyle="arc3,rad=0.3"))
        ax.text(4, 4.8, 'Nu⁻', color='blue', fontsize=10)
        
        ax.set_title('Carbonyl Nucleophilic Addition', color='white', fontsize=14)
        ax.axis('off')
        
        return save_plot_to_base64(plt.gcf())
        
    except Exception as e:
        print(f"Carbonyl mechanism error: {e}")
        return None

def create_general_mechanism(ax, parameters):
    """Create general chemical mechanism"""
    try:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        
        # Simple reaction coordinate diagram
        x = np.linspace(1, 9, 100)
        y = 2 + 3 * np.exp(-0.5*(x-5)**2)  # Energy barrier
        
        ax.plot(x, y, color='cyan', linewidth=3)
        
        # Labels
        ax.text(2, 1.5, 'Reactants', color='green', fontsize=12)
        ax.text(8, 1.5, 'Products', color='red', fontsize=12)
        ax.text(5, 5, 'Transition State', color='yellow', fontsize=10, ha='center')
        
        # Energy levels
        ax.axhline(y=2, color='white', linestyle='--', alpha=0.5)
        ax.text(1, 2.2, 'ΔG', color='orange', fontsize=10)
        
        ax.set_title('Reaction Coordinate Diagram', color='white', fontsize=14)
        ax.set_xlabel('Reaction Coordinate', color='white')
        ax.set_ylabel('Free Energy', color='white')
        ax.tick_params(colors='white')
        
        return save_plot_to_base64(plt.gcf())
        
    except Exception as e:
        print(f"General mechanism error: {e}")
        return None

def process_scientific_content(message):
    """Process scientific content including physics, biology, and chemistry"""
    scientific_content = {
        'physics_visualizations': [],
        'biology_visualizations': [],
        'chemical_mechanisms': [],
        'physics_calculations': [],
        'biology_calculations': [],
        'latex_equations': [],
        'calculations': []
    }
    
    try:
        message_lower = message.lower()
        
        # Physics detection and visualization
        physics_keywords = {
            'force': 'mechanics', 'motion': 'mechanics', 'kinematics': 'mechanics',
            'optics': 'optics', 'light': 'optics', 'lens': 'optics',
            'electric': 'electricity', 'circuit': 'electricity', 'magnetic': 'electricity',
            'wave': 'waves', 'sound': 'waves', 'thermodynamics': 'thermodynamics'
        }
        
        for keyword, physics_type in physics_keywords.items():
            if keyword in message_lower:
                visualization = create_physics_visualization(physics_type)
                if visualization:
                    scientific_content['physics_visualizations'].append({
                        'type': physics_type,
                        'image': visualization
                    })
                break
        
        # Biology detection and visualization
        biology_keywords = {
            'cell': 'cell', 'dna': 'dna', 'krebs': 'krebs_cycle',
            'ecosystem': 'ecosystem', 'neuron': 'neuron', 'biology': 'general'
        }
        
        for keyword, biology_type in biology_keywords.items():
            if keyword in message_lower:
                visualization = create_biology_visualization(biology_type)
                if visualization:
                    scientific_content['biology_visualizations'].append({
                        'type': biology_type,
                        'image': visualization
                    })
                break
        
        # Chemical mechanisms detection
        mechanism_keywords = {
            'alkene': 'alkene_hydration', 'hydration': 'alkene_hydration',
            'sn2': 'sn2', 'substitution': 'sn2',
            'electrophilic': 'electrophilic_aromatic', 'aromatic': 'electrophilic_aromatic',
            'carbonyl': 'carbonyl', 'mechanism': 'general'
        }
        
        for keyword, mechanism_type in mechanism_keywords.items():
            if keyword in message_lower:
                visualization = create_chemical_mechanism_visualization(mechanism_type)
                if visualization:
                    scientific_content['chemical_mechanisms'].append({
                        'type': mechanism_type,
                        'image': visualization
                    })
                break
        
        return scientific_content
        
    except Exception as e:
        print(f"Scientific content processing error: {e}")
        return scientific_content

def format_scientific_response(scientific_content):
    """Format scientific content for response"""
    response_parts = []
    
    # Add physics visualizations
    if scientific_content['physics_visualizations']:
        response_parts.append("**⚛️ PHYSICS DIAGRAMS:**\n")
        for viz in scientific_content['physics_visualizations']:
            response_parts.append(f"![{viz['type'].title()} Physics]({viz['image']})")
    
    # Add biology visualizations
    if scientific_content['biology_visualizations']:
        response_parts.append("**🧬 BIOLOGY DIAGRAMS:**\n")
        for viz in scientific_content['biology_visualizations']:
            response_parts.append(f"![{viz['type'].title()} Biology]({viz['image']})")
    
    # Add chemical mechanisms
    if scientific_content['chemical_mechanisms']:
        response_parts.append("**⚗️ CHEMICAL MECHANISMS:**\n")
        for mechanism in scientific_content['chemical_mechanisms']:
            response_parts.append(f"![{mechanism['type'].title()} Mechanism]({mechanism['image']})")
    
    return "\n\n".join(response_parts) if response_parts else None