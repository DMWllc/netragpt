import re
import sympy as sp # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
from io import BytesIO
import base64
import math
from matplotlib.patches import Circle, Rectangle # type: ignore

def render_latex_equation(latex_code):
    """Render LaTeX equation to base64 image"""
    try:
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif', size=14)
        
        fig = plt.figure(figsize=(8, 2))
        plt.axis('off')
        
        # Render the LaTeX equation
        plt.text(0.5, 0.5, f'${latex_code}$', 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=plt.gca().transAxes)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                    pad_inches=0.5, transparent=True)
        plt.close(fig)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"LaTeX rendering error: {e}")
        return None

def create_geometric_diagram(shape_type, parameters=None):
    """Create geometric shape diagrams"""
    try:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        ax.set_facecolor('#0f0f23')
        fig.patch.set_facecolor('#0f0f23')
        
        if shape_type == 'triangle':
            # Draw a triangle
            triangle = np.array([[0, 0], [1, 0], [0.5, 0.866], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'cyan', linewidth=3)
            ax.fill(triangle[:, 0], triangle[:, 1], alpha=0.3, color='cyan')
            ax.set_title('Triangle', color='white', fontsize=16)
            
            # Add labels
            ax.text(0, -0.1, 'A', color='white', fontsize=12, ha='center')
            ax.text(1, -0.1, 'B', color='white', fontsize=12, ha='center')
            ax.text(0.5, 0.9, 'C', color='white', fontsize=12, ha='center')
            
        elif shape_type == 'circle':
            # Draw a circle
            circle = plt.Circle((0.5, 0.5), 0.4, fill=False, color='magenta', linewidth=3)
            ax.add_patch(circle)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title('Circle', color='white', fontsize=16)
            
            # Add radius
            ax.plot([0.5, 0.9], [0.5, 0.5], 'yellow', linewidth=2, linestyle='--')
            ax.text(0.7, 0.45, 'r', color='yellow', fontsize=12)
            
        elif shape_type == 'rectangle':
            # Draw a rectangle
            rect = plt.Rectangle((0.2, 0.2), 0.6, 0.4, fill=False, color='lime', linewidth=3)
            ax.add_patch(rect)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title('Rectangle', color='white', fontsize=16)
            
            # Add dimensions
            ax.text(0.5, 0.1, 'width', color='white', fontsize=10, ha='center')
            ax.text(1.1, 0.4, 'height', color='white', fontsize=10, va='center')
            
        elif shape_type == 'function_plot':
            # Plot mathematical functions
            x = np.linspace(-2*np.pi, 2*np.pi, 1000)
            ax.plot(x, np.sin(x), 'cyan', label='sin(x)', linewidth=2)
            ax.plot(x, np.cos(x), 'magenta', label='cos(x)', linewidth=2)
            ax.axhline(y=0, color='white', linewidth=0.5)
            ax.axvline(x=0, color='white', linewidth=0.5)
            ax.grid(True, alpha=0.3, color='gray')
            ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
            ax.set_title('Trigonometric Functions', color='white', fontsize=16)
            ax.set_xlabel('x', color='white')
            ax.set_ylabel('f(x)', color='white')
            ax.tick_params(colors='white')
            
        elif shape_type == 'coordinate_system':
            # Coordinate system with vectors
            ax.axhline(y=0, color='white', linewidth=1)
            ax.axvline(x=0, color='white', linewidth=1)
            ax.grid(True, alpha=0.3, color='gray')
            
            # Draw some vectors
            ax.arrow(0, 0, 2, 1, head_width=0.1, head_length=0.1, fc='cyan', ec='cyan')
            ax.arrow(0, 0, 1, 2, head_width=0.1, head_length=0.1, fc='magenta', ec='magenta')
            
            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 3)
            ax.set_title('Coordinate System', color='white', fontsize=16)
            ax.set_xlabel('x', color='white')
            ax.set_ylabel('y', color='white')
            ax.tick_params(colors='white')
            
        # Style the plot
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white') 
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                    facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Geometric diagram error: {e}")
        return None

def create_mathematical_visualization(visualization_type, parameters=None):
    """Create various mathematical visualizations"""
    try:
        if visualization_type == 'function':
            return plot_mathematical_function(parameters)
        elif visualization_type == 'geometry':
            return create_geometric_diagram(parameters.get('shape', 'triangle'))
        elif visualization_type == 'vector':
            # Use coordinate_system diagram for vector visualization
            return create_geometric_diagram('coordinate_system')
        elif visualization_type == 'coordinate':
            return create_geometric_diagram('coordinate_system')
        else:
            return create_geometric_diagram('function_plot')
            
    except Exception as e:
        print(f"Mathematical visualization error: {e}")
        return None

def plot_mathematical_function(parameters):
    """Plot mathematical functions with proper styling"""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('#0f0f23')
        fig.patch.set_facecolor('#0f0f23')
        
        x = np.linspace(-2*np.pi, 2*np.pi, 1000)
        
        # Plot multiple functions
        functions = [
            ('sin(x)', np.sin(x), 'cyan'),
            ('cos(x)', np.cos(x), 'magenta'),
            ('tan(x)', np.tan(x), 'yellow')
        ]
        
        for label, y, color in functions:
            # Handle asymptotes for tan(x)
            if 'tan' in label:
                y = np.tan(x)
                y[np.abs(y) > 10] = np.nan
            ax.plot(x, y, color=color, label=label, linewidth=2)
        
        # Style the plot
        ax.axhline(y=0, color='white', linewidth=0.8)
        ax.axvline(x=0, color='white', linewidth=0.8)
        ax.grid(True, alpha=0.2, color='gray')
        
        ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white', 
                 loc='upper right', fontsize=12)
        
        ax.set_title('Mathematical Functions', color='white', fontsize=16, pad=20)
        ax.set_xlabel('x', color='white', fontsize=14)
        ax.set_ylabel('f(x)', color='white', fontsize=14)
        ax.tick_params(colors='white', labelsize=10)
        
        # Style spines
        for spine in ax.spines.values():
            spine.set_color('white')
            spine.set_linewidth(1)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Function plotting error: {e}")
        return None

def perform_advanced_calculation(expression):
    """Perform advanced mathematical calculations using sympy"""
    try:
        # Clean the expression
        expr_clean = expression.replace('×', '*').replace('÷', '/').replace('^', '**')
        
        # Parse using sympy
        sympy_expr = sp.sympify(expr_clean)
        
        # Evaluate
        result = sympy_expr.evalf()
        
        # Generate step-by-step solution
        steps = []
        
        # Show original expression
        steps.append(f"Expression: {sp.latex(sympy_expr)}")
        
        # Show simplified form if different
        simplified = sp.simplify(sympy_expr)
        if simplified != sympy_expr:
            steps.append(f"Simplified: {sp.latex(simplified)}")
        
        # Show result
        steps.append(f"Result: {sp.latex(result)}")
        
        return {
            'expression': expression,
            'result': str(result),
            'latex_result': sp.latex(result),
            'steps': steps,
            'type': 'advanced'
        }
        
    except Exception as e:
        print(f"Advanced calculation error: {e}")
        return None

def perform_calculation(expression):
    """Perform mathematical calculations safely"""
    try:
        # Clean the expression
        expression = expression.replace('×', '*').replace('÷', '/').replace('^', '**')
        
        # Remove any non-math characters for safety
        safe_chars = set('0123456789+-*/.()% ')
        clean_expression = ''.join(char for char in expression if char in safe_chars)
        
        if not clean_expression:
            return None
            
        # Evaluate the expression safely
        result = eval(clean_expression, {"__builtins__": None}, {})
        
        return {
            'expression': expression,
            'result': result,
            'formatted': f"{expression} = {result}"
        }
        
    except Exception as e:
        print(f"Calculation error: {e}")
        return None

def handle_calculations(query):
    """Handle mathematical calculations and problem solving"""
    query_lower = query.lower()
    
    # Math calculation patterns
    calculation_patterns = [
        r'calculate (.+)',
        r'what is (.+)',
        r'solve (.+)',
        r'compute (.+)',
        r'(.+) equals',
        r'(.+) ='
    ]
    
    for pattern in calculation_patterns:
        match = re.search(pattern, query_lower)
        if match:
            expression = match.group(1).strip()
            # Remove question marks and other non-math chars
            expression = re.sub(r'[?\s]+', '', expression)
            
            result = perform_calculation(expression)
            if result:
                return f"🧮 Calculation Result:\n```\n{result['formatted']}\n```"
    
    # Special calculations
    if 'percentage' in query_lower:
        percentage_match = re.search(r'(\d+)% of (\d+)', query_lower)
        if percentage_match:
            percentage = float(percentage_match.group(1))
            number = float(percentage_match.group(2))
            result = (percentage / 100) * number
            return f"🧮 Percentage Calculation:\n```\n{percentage}% of {number} = {result}\n```"
    
    # Area calculations
    if 'area' in query_lower:
        if 'circle' in query_lower:
            radius_match = re.search(r'radius[^\d]*(\d+)', query_lower)
            if radius_match:
                radius = float(radius_match.group(1))
                area = math.pi * radius ** 2
                return f"🧮 Circle Area:\n```\nArea = π × r² = {math.pi:.2f} × {radius}² = {area:.2f}\n```"
    
    return None

def process_mathematical_content(message):
    """Process mathematical content including LaTeX and visualizations"""
    mathematical_content = {
        'latex_equations': [],
        'visualizations': [],
        'calculations': []
    }
    
    try:
        # Detect LaTeX expressions
        latex_patterns = [
            r'\\\[(.*?)\\\]',  # \[...\]
            r'\\\((.*?)\\\)',  # \(...\)
            r'\$\$(.*?)\$\$',  # $$...$$
            r'\$(.*?)\$'       # $...$
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, message, re.DOTALL)
            for match in matches:
                if match.strip():
                    rendered_image = render_latex_equation(match.strip())
                    if rendered_image:
                        mathematical_content['latex_equations'].append({
                            'latex': match.strip(),
                            'image': rendered_image
                        })
        
        # Detect visualization requests
        viz_keywords = {
            'graph': 'function',
            'plot': 'function', 
            'diagram': 'geometry',
            'visualize': 'geometry',
            'draw': 'geometry',
            'shape': 'geometry',
            'coordinate': 'coordinate',
            'vector': 'vector'
        }
        
        for keyword, viz_type in viz_keywords.items():
            if keyword in message.lower():
                visualization = create_mathematical_visualization(viz_type)
                if visualization:
                    mathematical_content['visualizations'].append({
                        'type': viz_type,
                        'image': visualization
                    })
                break
        
        # Detect calculations
        calc_patterns = [
            r'calculate\s+(.+)',
            r'compute\s+(.+)',
            r'solve\s+(.+)',
            r'what is\s+(.+)',
            r'(\d+[\+\-\*\/\^]\d+)'
        ]
        
        for pattern in calc_patterns:
            matches = re.findall(pattern, message.lower())
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                calculation_result = perform_advanced_calculation(match.strip())
                if calculation_result:
                    mathematical_content['calculations'].append(calculation_result)
        
        return mathematical_content
        
    except Exception as e:
        print(f"Mathematical content processing error: {e}")
        return mathematical_content

def format_mathematical_response(math_content):
    """Format mathematical content for response"""
    response_parts = []
    
    # Add calculations
    if math_content['calculations']:
        response_parts.append("**🧮 CALCULATIONS:**\n")
        for calc in math_content['calculations']:
            response_parts.append(f"```\n{calc['expression']} = {calc['result']}\n```")
    
    # Add LaTeX equations
    if math_content['latex_equations']:
        response_parts.append("**📐 MATHEMATICAL EXPRESSIONS:**\n")
        for eq in math_content['latex_equations']:
            response_parts.append(f"![Equation]({eq['image']})")
    
    # Add visualizations
    if math_content['visualizations']:
        response_parts.append("**📊 VISUALIZATIONS:**\n")
        for viz in math_content['visualizations']:
            response_parts.append(f"![{viz['type'].title()}]({viz['image']})")
    
    return "\n\n".join(response_parts) if response_parts else None

def format_code_response(code, language=''):
    """Format code blocks for proper display"""
    if language:
        return f"```{language}\n{code}\n```"
    else:
        return f"```\n{code}\n```"