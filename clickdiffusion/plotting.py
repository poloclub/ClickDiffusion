from PIL import Image
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches
# Set up latex backend for colored text
# import matplotlib
# matplotlib.use('ps')

# from matplotlib import rc
# rc('text',usetex=True)
# rc('text.latex', preamble='\\usepackage{color}')

def visualize_visual_instruction(instruction, ax=None, image_size=(512, 512), save_path=""):
    """
    Given an instruction (which may or may not be visual), visualize it.
    """
    # Create white PIL background
    background = Image.new("RGB", image_size, (255, 255, 255))
    ax.imshow(background)
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    # Display the image
    ax.imshow(background)
    # Extract each of the boxes from the instruction
    pattern = r'\{([^}]+)\}'
    # result = [s for s in re.split(pattern, instruction) if s]
    result = re.findall(pattern, instruction)
    # Assign each one a color
    # colors = ["red", "blue"]
    # colored_instruction = ""
    for substring in result:
        substring = "{" + substring + "}"
        if substring.startswith("{") and substring.endswith("}"):
            # Get the color
            # color = colors.pop()
            # Add the color to the substring
            # colored_instruction = r'\textcolor{red}{Today}'
            # colored_instruction += substring
            # Check if it is a box or a point
            if 'width' in substring:
                # Draw the box
                box = eval(substring)
                # Rescale to image size
                x = int(box['x'] * image_size[0])
                y = int(box['y'] * image_size[1])
                width = int(box['width'] * image_size[0])
                height = int(box['height'] * image_size[1])
                # Create a Rectangle patch
                rect = patches.Rectangle(
                    (x, y),
                    width,
                    height,
                    linewidth=1, 
                    edgecolor='r', 
                    facecolor='none'
                )
                # Add the patch to the Axes
                ax.add_patch(rect)
            else:
                # Draw the point
                point = eval(substring)
                # Rescale to image size
                x = int(point['x'] * image_size[0])
                y = int(point['y'] * image_size[1])
                # Create a Circle patch
                point = patches.Circle(
                    (x, y),
                    radius=5,
                    linewidth=1, 
                    edgecolor='r', 
                    facecolor='r'
                )
                # Add the patch to the Axes
                ax.add_patch(point)
            
        # else:
        # colored_instruction += substring
    # Set the title
    ax.set_title(instruction, fontsize=20)

def visualize_scene_graph(scene_graph, image_size=(512, 512), input_ax=None, save_path="scene_graph_vis.png"):
    """
    Visualize a scene graph.

    Args:
        scene_graph: A scene graph dictionary.
    """
    # Create white PIL background
    background = Image.new("RGB", image_size, (255,255,255))
    # Create figure and axes
    if input_ax is None:
        fig, ax = plt.subplots()
    else: 
        ax = input_ax
    # Remove axis ticks
    ax.set_xticks([])
    ax.set_yticks([])
    # Add a title to the plot
    # ax.set_title(scene_graph["prompt"])
    # Display the image
    ax.imshow(background)
    # Iterate through each box and visualize it
    boxes = scene_graph["boxes"]
    for box_object in boxes:
        # Box dimensions
        box_name = box_object["name"]
        box = box_object["box"]
        # Rescale to image size
        x = int(box['x'] * image_size[0])
        y = int(box['y'] * image_size[1])
        width = int(box['width'] * image_size[0])
        height = int(box['height'] * image_size[1])
        # Create a Rectangle patch
        rect = patches.Rectangle(
            (x, y),
            width,
            height,
            linewidth=1, 
            edgecolor='r', 
            facecolor='none'
        )
        # Add the patch to the Axes
        ax.add_patch(rect)
        # Add label below box
        ax.text(x, y + 20, box_name, fontsize=16)

    if input_ax is None:
        plt.savefig(save_path)
    else:
        return ax

def plot_instruction_example(text_instruction, input_scene_graph, output_scene_graph, save_path=""):
    """
        Plot a the given instruction. 
    """
    fig, axs = plt.subplots(1, 3, figsize=(24, 8))
    plt.suptitle(f"Instruction: {text_instruction}", fontsize=24)
    # Visualize input scene graph
    visualize_scene_graph(input_scene_graph, input_ax=axs[0])
    axs[0].set_title("Input Scene Graph", fontsize=20)
    # Visualize the instruction
    visualize_visual_instruction(text_instruction, ax=axs[1])
    # Visualize output scene graph
    visualize_scene_graph(output_scene_graph, input_ax=axs[2])
    axs[2].set_title("Output Scene Graph", fontsize=20)
    # Save the plot
    plt.savefig(save_path)
