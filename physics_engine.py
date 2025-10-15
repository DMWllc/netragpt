import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from io import BytesIO
import base64
import sympy as sp # type: ignore
from matplotlib.patches import Circle, Rectangle, Arrow, FancyArrowPatch, Polygon, Arc # type: ignore

class PhysicsEngine:
    def __init__(self):
        self.physical_constants = {
            'c': 299792458,  # Speed of light (m/s)
            'G': 6.67430e-11,  # Gravitational constant
            'h': 6.62607015e-34,  # Planck's constant
            'k_B': 1.380649e-23,  # Boltzmann constant
            'e': 1.60217662e-19,  # Electron charge
            'm_e': 9.10938356e-31,  # Electron mass
            'm_p': 1.6726219e-27,  # Proton mass
            'ε0': 8.854187817e-12,  # Vacuum permittivity
            'μ0': 1.25663706212e-6,  # Vacuum permeability
            'g': 9.81  # Gravitational acceleration (m/s²)
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
    
    def create_mechanics_diagram(self, diagram_type, parameters=None):
        """Create mechanics diagrams"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_facecolor('#0f0f23')
            fig.patch.set_facecolor('#0f0f23')
            
            if diagram_type == 'projectile_motion':
                return self._create_projectile_motion(ax, parameters, fig)
            elif diagram_type == 'forces':
                return self._create_force_diagram(ax, parameters, fig)
            elif diagram_type == 'pendulum':
                return self._create_pendulum_diagram(ax, parameters, fig)
            elif diagram_type == 'spring_mass':
                return self._create_spring_mass_diagram(ax, parameters, fig)
            elif diagram_type == 'inclined_plane':
                return self._create_inclined_plane_diagram(ax, parameters, fig)
            elif diagram_type == 'circular_motion':
                return self._create_circular_motion_diagram(ax, parameters, fig)
            elif diagram_type == 'collisions':
                return self._create_collision_diagram(ax, parameters, fig)
                
        except Exception as e:
            print(f"Mechanics diagram error: {e}")
            return None

    def _create_collision_diagram(self, ax, parameters, fig):
        """Create collision diagram"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Before collision
        ax.text(2.5, 9, 'Before Collision', color='yellow', fontsize=12, ha='center')
        circle1_before = Circle((2, 6), 0.5, color='red', alpha=0.7)
        circle2_before = Circle((4, 6), 0.5, color='blue', alpha=0.7)
        ax.add_patch(circle1_before)
        ax.add_patch(circle2_before)
        
        # Velocity arrows before collision
        ax.arrow(2, 6, 1, 0, head_width=0.2, head_length=0.2, fc='red', ec='red')
        ax.arrow(4, 6, -0.5, 0, head_width=0.2, head_length=0.2, fc='blue', ec='blue')
        
        # Collision moment
        ax.text(5, 9, 'Collision', color='orange', fontsize=12, ha='center')
        circle_collision = Circle((5, 6), 0.6, color='yellow', alpha=0.5)
        ax.add_patch(circle_collision)
        
        # After collision
        ax.text(7.5, 9, 'After Collision', color='green', fontsize=12, ha='center')
        circle1_after = Circle((7, 6), 0.5, color='red', alpha=0.7)
        circle2_after = Circle((8, 6), 0.5, color='blue', alpha=0.7)
        ax.add_patch(circle1_after)
        ax.add_patch(circle2_after)
        
        # Velocity arrows after collision
        ax.arrow(7, 6, -0.3, 0, head_width=0.2, head_length=0.2, fc='red', ec='red')
        ax.arrow(8, 6, 0.8, 0, head_width=0.2, head_length=0.2, fc='blue', ec='blue')
        
        # Conservation laws
        ax.text(5, 3, 'Conservation of Momentum: m₁v₁ + m₂v₂ = m₁v₁\' + m₂v₂\'', 
               color='cyan', fontsize=10, ha='center')
        ax.text(5, 2, 'Conservation of Energy (elastic): ½m₁v₁² + ½m₂v₂² = ½m₁v₁\'² + ½m₂v₂\'²', 
               color='cyan', fontsize=9, ha='center')
        
        ax.set_title('Elastic Collision Diagram', color='white', fontsize=14)
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)

    def _create_spring_mass_diagram(self, ax, parameters, fig):
        """Create spring-mass system diagram"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Spring
        x_spring = np.linspace(1, 3, 100)
        y_spring = 5 + 0.3 * np.sin(10 * x_spring)
        ax.plot(x_spring, y_spring, 'white', linewidth=3)
        
        # Mass
        mass = Rectangle((3, 4), 1, 2, fill=True, color='cyan', alpha=0.7)
        ax.add_patch(mass)
        
        # Wall
        ax.plot([1, 1], [3, 7], 'gray', linewidth=4)
        
        # Equilibrium position
        ax.axhline(y=5, color='yellow', linestyle='--', alpha=0.5)
        ax.text(5, 5.2, 'Equilibrium Position', color='yellow', fontsize=10)
        
        # Displacement arrow
        ax.arrow(4.5, 5, 1, 0, head_width=0.2, head_length=0.2, fc='magenta', ec='magenta')
        ax.text(5, 4.5, 'Displacement (x)', color='magenta', fontsize=10)
        
        # Restoring force arrow
        ax.arrow(3.5, 5, -0.8, 0, head_width=0.2, head_length=0.2, fc='red', ec='red')
        ax.text(2.5, 5.5, 'Restoring Force F = -kx', color='red', fontsize=10)
        
        ax.set_title('Spring-Mass System (Simple Harmonic Motion)', color='white', fontsize=14)
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)

    def _create_force_diagram(self, ax, parameters, fig):
        """Create force diagram"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Object
        rect = Rectangle((4, 4), 2, 2, fill=True, color='cyan', alpha=0.7)
        ax.add_patch(rect)
        
        # Forces with better positioning
        forces = {
            'gravity': {'pos': (5, 4), 'vec': (0, -1.5), 'color': 'red', 'label': 'Fg = mg'},
            'normal': {'pos': (5, 6), 'vec': (0, 1.2), 'color': 'blue', 'label': 'Fn'},
            'applied': {'pos': (4, 5), 'vec': (-1, 0), 'color': 'green', 'label': 'Fa'},
            'friction': {'pos': (6, 5), 'vec': (0.8, 0), 'color': 'orange', 'label': 'Ff'}
        }
        
        for force_name, force_data in forces.items():
            pos = force_data['pos']
            vec = force_data['vec']
            ax.arrow(pos[0], pos[1], vec[0], vec[1], 
                    head_width=0.2, head_length=0.2, 
                    fc=force_data['color'], ec=force_data['color'], linewidth=2)
            ax.text(pos[0] + vec[0] + 0.2, pos[1] + vec[1], 
                   force_data['label'], color=force_data['color'], fontsize=10)
        
        # Net force
        ax.arrow(5, 3, 0.3, 0, head_width=0.15, head_length=0.15, fc='magenta', ec='magenta')
        ax.text(5.5, 2.8, 'Net Force → Acceleration', color='magenta', fontsize=10)
        
        ax.set_title('Force Diagram - Newton\'s Laws of Motion', color='white', fontsize=14)
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)

    def create_electromagnetism_diagram(self, diagram_type, parameters=None):
        """Create electromagnetism diagrams"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.set_facecolor('#0f0f23')
            fig.patch.set_facecolor('#0f0f23')
            
            if diagram_type == 'electric_field':
                return self._create_electric_field(ax, parameters, fig)
            elif diagram_type == 'magnetic_field':
                return self._create_magnetic_field(ax, parameters, fig)
            elif diagram_type == 'circuit':
                return self._create_circuit_diagram(ax, parameters, fig)
                
        except Exception as e:
            print(f"Electromagnetism diagram error: {e}")
            return None

    def _create_electric_field(self, ax, parameters, fig):
        """Create electric field diagram"""
        # Create grid
        x = np.linspace(-5, 5, 20)
        y = np.linspace(-5, 5, 20)
        X, Y = np.meshgrid(x, y)
        
        # Point charge at origin
        charge_strength = parameters.get('charge', 1)
        
        # Electric field calculation
        R = np.sqrt(X**2 + Y**2)
        Ex = charge_strength * X / R**3
        Ey = charge_strength * Y / R**3
        
        # Remove singularities at origin
        Ex[R < 0.5] = 0
        Ey[R < 0.5] = 0
        
        # Plot field lines
        ax.streamplot(X, Y, Ex, Ey, color='cyan', linewidth=1, density=2)
        
        # Plot charge
        charge_color = 'red' if charge_strength > 0 else 'blue'
        charge_size = abs(charge_strength) * 100
        ax.scatter(0, 0, c=charge_color, s=charge_size, alpha=0.7)
        
        # Charge label
        charge_sign = '+' if charge_strength > 0 else '-'
        ax.text(0.5, 0.5, f'{charge_sign} charge', color=charge_color, fontsize=12)
        
        ax.set_xlabel('X Position', color='white')
        ax.set_ylabel('Y Position', color='white')
        ax.set_title('Electric Field Lines', color='white', fontsize=16)
        ax.tick_params(colors='white')
        
        return self.save_plot_to_base64(fig)

    def _create_magnetic_field(self, ax, parameters, fig):
        """Create magnetic field diagram"""
        # Create grid around a current-carrying wire
        x = np.linspace(-5, 5, 20)
        y = np.linspace(-5, 5, 20)
        X, Y = np.meshgrid(x, y)
        
        # Magnetic field around wire (circular)
        R = np.sqrt(X**2 + Y**2)
        Bx = -Y / R**2  # Magnetic field components
        By = X / R**2
        
        # Remove singularity at origin
        Bx[R < 0.5] = 0
        By[R < 0.5] = 0
        
        # Plot field lines
        ax.streamplot(X, Y, Bx, By, color='orange', linewidth=1, density=2)
        
        # Draw wire
        ax.plot([0, 0], [-5, 5], 'red', linewidth=3, label='Current-carrying wire')
        
        # Current direction
        ax.arrow(0, 4, 0, -1, head_width=0.3, head_length=0.3, fc='yellow', ec='yellow')
        ax.text(0.5, 3.5, 'Current (I)', color='yellow', fontsize=10)
        
        ax.set_xlabel('X Position', color='white')
        ax.set_ylabel('Y Position', color='white')
        ax.set_title('Magnetic Field Around Current-Carrying Wire', color='white', fontsize=14)
        ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
        ax.tick_params(colors='white')
        
        return self.save_plot_to_base64(fig)

    def _create_circuit_diagram(self, ax, parameters, fig):
        """Create simple circuit diagram"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        
        # Battery
        ax.plot([2, 2], [4, 6], 'red', linewidth=4)
        ax.plot([2.3, 2.3], [4, 6], 'black', linewidth=4)
        ax.text(1.5, 7, 'Battery', color='red', fontsize=10)
        
        # Resistor
        ax.plot([4, 6], [5, 5], 'brown', linewidth=3)
        ax.plot([4.5, 4.5], [4.5, 5.5], 'brown', linewidth=2)
        ax.plot([5, 5], [4.5, 5.5], 'brown', linewidth=2)
        ax.plot([5.5, 5.5], [4.5, 5.5], 'brown', linewidth=2)
        ax.text(4.5, 6, 'Resistor', color='orange', fontsize=10)
        
        # Wires
        ax.plot([2.3, 4], [5, 5], 'yellow', linewidth=2)  # Top wire
        ax.plot([6, 8], [5, 5], 'yellow', linewidth=2)    # Bottom wire
        ax.plot([8, 2], [5, 5], 'yellow', linewidth=2)    # Return wire
        
        # Current direction
        ax.arrow(3, 5, 0.5, 0, head_width=0.2, head_length=0.2, fc='cyan', ec='cyan')
        ax.text(3, 5.5, 'Current (I)', color='cyan', fontsize=10)
        
        # Voltage label
        ax.text(5, 3, 'V = IR (Ohm\'s Law)', color='white', fontsize=12,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='blue', alpha=0.5))
        
        ax.set_title('Simple Electric Circuit', color='white', fontsize=14)
        ax.axis('off')
        
        return self.save_plot_to_base64(fig)

    def calculate_energy(self, parameters):
        """Perform energy calculations"""
        try:
            calculation_type = parameters.get('type', 'kinetic')
            
            if calculation_type == 'kinetic':
                m = parameters.get('mass', 0)
                v = parameters.get('velocity', 0)
                return {'kinetic_energy': 0.5 * m * v**2}
                
            elif calculation_type == 'potential':
                m = parameters.get('mass', 0)
                h = parameters.get('height', 0)
                g = 9.81
                return {'potential_energy': m * g * h}
                
            elif calculation_type == 'spring':
                k = parameters.get('spring_constant', 0)
                x = parameters.get('displacement', 0)
                return {'spring_energy': 0.5 * k * x**2}
                
            elif calculation_type == 'mechanical':
                m = parameters.get('mass', 0)
                v = parameters.get('velocity', 0)
                h = parameters.get('height', 0)
                g = 9.81
                ke = 0.5 * m * v**2
                pe = m * g * h
                return {
                    'kinetic_energy': ke,
                    'potential_energy': pe,
                    'total_mechanical_energy': ke + pe
                }
                
        except Exception as e:
            print(f"Energy calculation error: {e}")
            return None

    def calculate_kinematics(self, parameters):
        """Perform kinematics calculations"""
        try:
            calculation_type = parameters.get('type', 'projectile')
            
            if calculation_type == 'projectile':
                v0 = parameters.get('initial_velocity', 0)
                angle = np.radians(parameters.get('angle', 0))
                g = 9.81
                
                results = {
                    'time_of_flight': (2 * v0 * np.sin(angle)) / g,
                    'maximum_height': (v0**2 * np.sin(angle)**2) / (2 * g),
                    'range': (v0**2 * np.sin(2 * angle)) / g,
                    'maximum_range_angle': '45 degrees',
                    'initial_velocity_x': v0 * np.cos(angle),
                    'initial_velocity_y': v0 * np.sin(angle)
                }
                return results
                
            elif calculation_type == 'free_fall':
                h = parameters.get('height', 0)
                g = 9.81
                
                results = {
                    'time_to_fall': np.sqrt(2 * h / g),
                    'impact_velocity': np.sqrt(2 * g * h)
                }
                return results
                
            elif calculation_type == 'inclined_plane':
                angle = np.radians(parameters.get('angle', 0))
                mass = parameters.get('mass', 0)
                g = 9.81
                
                results = {
                    'acceleration': g * np.sin(angle),
                    'normal_force': mass * g * np.cos(angle),
                    'parallel_force': mass * g * np.sin(angle)
                }
                return results
                
        except Exception as e:
            print(f"Kinematics calculation error: {e}")
            return None

    def process_physics_query(self, message):
        """Process physics-related queries"""
        physics_content = {
            'visualizations': [],
            'calculations': [],
            'explanations': [],
            'constants': []
        }
        
        message_lower = message.lower()
        
        # Mechanics detection
        mechanics_keywords = {
            'projectile': 'projectile_motion',
            'force': 'forces', 
            'kinematics': 'projectile_motion',
            'pendulum': 'pendulum',
            'spring': 'spring_mass',
            'inclined plane': 'inclined_plane',
            'ramp': 'inclined_plane',
            'slope': 'inclined_plane',
            'circular motion': 'circular_motion',
            'centripetal': 'circular_motion',
            'collision': 'collisions'
        }
        
        # Electromagnetism detection
        em_keywords = {
            'electric field': 'electric_field',
            'magnetic field': 'magnetic_field', 
            'circuit': 'circuit',
            'voltage': 'circuit',
            'current': 'circuit',
            'resistor': 'circuit'
        }
        
        # Create visualizations
        for keyword, diagram_type in mechanics_keywords.items():
            if keyword in message_lower:
                params = {}
                
                # Extract parameters from message
                if 'angle' in message_lower:
                    if '30' in message_lower:
                        params['angle'] = 30
                    elif '45' in message_lower:
                        params['angle'] = 45
                    elif '60' in message_lower:
                        params['angle'] = 60
                
                if 'mass' in message_lower or 'kg' in message_lower:
                    if '5' in message_lower:
                        params['mass'] = 5
                    elif '10' in message_lower:
                        params['mass'] = 10
                
                visualization = self.create_mechanics_diagram(diagram_type, params)
                if visualization:
                    physics_content['visualizations'].append({
                        'type': diagram_type,
                        'image': visualization
                    })
        
        for keyword, diagram_type in em_keywords.items():
            if keyword in message_lower:
                visualization = self.create_electromagnetism_diagram(diagram_type)
                if visualization:
                    physics_content['visualizations'].append({
                        'type': diagram_type,
                        'image': visualization
                    })
        
        # Perform calculations
        if any(word in message_lower for word in ['calculate', 'compute', 'solve']):
            if any(word in message_lower for word in ['velocity', 'acceleration', 'projectile']):
                calc_result = self.calculate_kinematics({'type': 'projectile'})
                if calc_result:
                    physics_content['calculations'].append(calc_result)
            
            if any(word in message_lower for word in ['energy', 'kinetic', 'potential']):
                calc_result = self.calculate_energy({'type': 'kinetic'})
                if calc_result:
                    physics_content['calculations'].append(calc_result)
            
            if any(word in message_lower for word in ['inclined', 'ramp', 'slope']):
                calc_result = self.calculate_kinematics({'type': 'inclined_plane'})
                if calc_result:
                    physics_content['calculations'].append(calc_result)
        
        # Add physical constants if requested
        if any(word in message_lower for word in ['constant', 'gravity', 'speed of light']):
            physics_content['constants'] = self.physical_constants
        
        return physics_content

# Create global instance
physics_engine = PhysicsEngine()