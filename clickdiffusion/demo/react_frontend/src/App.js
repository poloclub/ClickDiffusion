import './App.css';
import { Tldraw, track, useEditor, TLUiOverrides, toolbarItem, GeoShapeGeoStyle, Editor, AssetRecordType, DefaultColorStyle, forwardRef, createShapeId} from '@tldraw/tldraw'
import '@tldraw/tldraw/tldraw.css'
import { useEffect, useState, useRef, Component, createRef, useCallback, componentDidMount} from 'react'
import './custom-ui.css'

import activePointerIcon from "./tool_icons/active/pointer.svg"
import activeReloadIcon from "./tool_icons/active/reload.svg"
import activeRectangleIcon from "./tool_icons/active/rectangle.svg"
import activeStarIcon from "./tool_icons/active/star.svg"
import inactivePointerIcon from "./tool_icons/inactive/pointer.svg"
import inactiveReloadIcon from "./tool_icons/inactive/reload.svg"
import inactiveRectangleIcon from "./tool_icons/inactive/rectangle.svg"
import inactiveStarIcon from "./tool_icons/inactive/star.svg"

import parkImage from './backgrounds/park.png'
import drivewayImage from './backgrounds/driveway.jpeg'
import parkTable from './backgrounds/park_table.png'
import kitchenTable from './backgrounds/kitchen_table.jpeg'
import backyard from './backgrounds/BackYard.jpeg'

import loadingGIF from './tool_icons/loading-gif.gif'

// Access the environment variable 'REACT_APP_PORT'
const port = process.env.REACT_APP_BACKEND_PORT;

console.log("Port: ", port);

const tldrawWidth = 800;
const tldrawHeight = 750;
const imageWidth = 500;
const imageHeight = 500;

// Default Backgrounds
const default_background_data = {
    "park": {
        "default_instruction": 'Add a border collie {"x": 0.05, "y": 0.3, "width": 0.4, "height": 0.65}',
		"default_layout": {
			"prompt": "A border collie in a park by a pine tree. ",
			"boxes": [
				{
					"unique_id": 1,
					"name": "pine tree",
					"box": {
						"x": 0.6,
						"y": 0.1,
						"width": 0.25,
						"height": 0.8
					}
				}
			], 
		},
        "background_image": parkImage
    },
	"backyard": {
		"default_instruction": 'Remove the golden retriever.',
		"default_layout": {
			"prompt": "A border collie, a golden retriever, and a red ball in a back yard. ",
			"boxes": [
				{
					"unique_id": 0,
					"name": "border collie",
					"box": {
						"x": 0.05,
						"y": 0.3,
						"width": 0.25,
						"height": 0.5
					}
				},
				{
					"unique_id": 1,
					"name": "golden retriever",
					"box": {
						"x": 0.7,
						"y": 0.4,
						"width": 0.25,
						"height": 0.4
					}
				},
				{
					"unique_id": 2,
					"name": "red ball",
					"box": {
						"x": 0.35,
						"y": 0.5,
						"width": 0.25,
						"height": 0.25
					}
				}
			]
		}, 
		"background_image": backyard
	},
	"driveway": {
		"default_instruction": 'Resize the truck to {"x": 0.3, "y": 0.2, "width": 0.5, "height": 0.6} and make it green.',
		"default_layout": {
			"prompt": "A red truck in a driveway. ",
			"boxes": [
				{
					"unique_id": 0,
					"name": "red truck",
					"box": {
						"x": 0.25,
						"y": 0.3,
						"width": 0.4,
						"height": 0.4
					}
				}
			]
		}, 
		"background_image": drivewayImage
	},
	"park_table": {
		"default_instruction": 'Remove the sliced apples in {"x": 0.3, "y": 0.45, "width": 0.45, "height": 0.25}',
		"default_layout": {
			"prompt": "a green apple, a red apple, a sliced green apple, a plate, a sliced red apple on a table.",
			"boxes": [
				{
					"unique_id": 0,
					"name": "a single apple", 
					"box": {
						"x": 0.1,
						"y": 0.6,
						"width": 0.15,
						"height": 0.15
					}
				},
				{
					"unique_id": 1,
					"name": "a single apple", 
					"box": {
						"x": 0.75,
						"y": 0.6,
						"width": 0.15,
						"height": 0.15
					}
				},
				{
					"unique_id": 2,
					"name": "a single green apple", 
					"box": {
						"x": 0.4,
						"y": 0.75,
						"width": 0.17,
						"height": 0.14
					}
				},
				{
					"unique_id": 3,
					"name": "a single green apple", 
					"box": {
						"x": 0.05,
						"y": 0.75,
						"width": 0.15,
						"height": 0.15
					}
				},
				{
					"unique_id": 4,
					"name": "a single green apple",
					"box": {
						"x": 0.6,
						"y": 0.75,
						"width": 0.15,
						"height": 0.15
					}
				},
				{
					"unique_id": 5,
					"name": "a single sliced green apple", 
					"box": {
						"x": 0.32,
						"y": 0.49,
						"width": 0.15,
						"height": 0.15
					}
				},
				{
					"unique_id": 6,
					"name": "a single sliced red apple", 
					"box": {
						"x": 0.53,
						"y": 0.49,
						"width": 0.18,
						"height": 0.15
					}
				},
				{
					"unique_id": 7,
					"name": "a plate", 
					"box": {
						"x": 0.3,
						"y": 0.6,
						"width": 0.5,
						"height": 0.15
					}
				},
			]
		}, 
		"background_image": parkTable
	},
	"kitchen_table": {
		"default_instruction": 'Remove the white cups in {"x":0.14,"y":0.75,"width":0.47,"height":0.24}',
		"default_layout": {
			"prompt": "White cup, black mug, white mug, white bowl, black mug, white mug on a table. ",
			"boxes": [
				{
					"unique_id": 0,
					"name": "black mug",
					"box": {
						"x": 0.1,
						"y": 0.65,
						"width": 0.15,
						"height": 0.2
					}
				},
				{
					"unique_id": 1,
					"name": "white mug",
					"box": {
						"x": 0.1,
						"y": 0.8,
						"width": 0.2,
						"height": 0.15
					}
				},
				{
					"unique_id": 2,
					"name": "white mug",
					"box": {
						"x": 0.25,
						"y": 0.85,
						"width": 0.17,
						"height": 0.15
					}
				},
				{
					"unique_id": 3,
					"name": "white bowl",
					"box": {
						"x": 0.3,
						"y": 0.6,
						"width": 0.4,
						"height": 0.2
					}
				},
				{
					"unique_id": 4,
					"name": "black mug",
					"box": {
						"x": 0.6,
						"y": 0.75,
						"width": 0.2,
						"height": 0.2
					}
				},
				{
					"unique_id": 5,
					"name": "white mug",
					"box": {
						"x": 0.85,
						"y": 0.7,
						"width": 0.15,
						"height": 0.2
					}
				}
			]
		}, 
		"background_image": kitchenTable
	}
}

const colorPalette = [
	"blue",
	"orange",
	"green"
];

function roundToTwoDigits(number) {
	return Math.round(number * 100) / 100;
}	


function getCurrentTool(editor) {
	// Figures out current tool from UI state. 
	if (editor.getCurrentToolId() == "select") {
		return "select";
	} else if (editor.getCurrentToolId() == "geo") {
		// Figure out if it is star or rectangle from the editor state
		const stylesForNextShape = editor.getInstanceState().stylesForNextShape;
		if (stylesForNextShape[GeoShapeGeoStyle.id] === "star") {
			return "star";
		} else if (stylesForNextShape[GeoShapeGeoStyle.id] === "rectangle") {
			return "rectangle";
		}
	}
}

// [2]
const Toolbar = track((props) => {
	const editor = useEditor()
	// Figure out the current tool 
	const currentTool = getCurrentTool(editor);
	// Make sure the camera can't be moved
	const pointerIcon = currentTool === 'select' ? activePointerIcon : inactivePointerIcon;
	// const eraserIcon = currentTool === 'eraser' ? activeEraserIcon : inactiveEraserIcon;
	// const arrowIcon = currentTool === 'arrow' ? activeArrowIcon : inactiveArrowIcon;
	const rectangleIcon = currentTool === 'rectangle' ? activeRectangleIcon : inactiveRectangleIcon;
	const starIcon = currentTool === 'star' ? activeStarIcon : inactiveStarIcon;
	const reloadIcon = currentTool === 'reload' ? activeReloadIcon : inactiveReloadIcon;
	const loading = props.loading;

	return (
		<div className={loading ? "custom-toolbar loading" : "custom-toolbar not-loading"}>
			{/* <img 
				className="custom-tool" 
				id="back-button" 
				src={backwardButtonIcon} 
				alt="pointer"
				draggable="false"
				onClick={() => {
					// 
				}}
			/>
			<img 
				className="custom-tool" 
				id="forward-button" 
				src={forwardButtonIcon} 
				alt="pointer"
				draggable="false"
				onClick={() => {
					// 
				}}
			/>
			<span className="vertical-bar"></span> */}
			<img
				onClick={() => {
					editor.setCurrentTool('select');
				}}
				className="custom-tool" 
				id="tool-select" 
				src={pointerIcon} 
				alt="select"
				draggable="false"
			/>
			<img
				onClick={() => {
					editor.updateInstanceState(
						{
							stylesForNextShape: {
								...editor.getInstanceState().stylesForNextShape,
								[GeoShapeGeoStyle.id]: "star",
							},
						},
						{ ephemeral: true }
					);
					// update the current color
					editor.setStyleForNextShapes(
						DefaultColorStyle, 
						props.currentColor
					);
					editor.setCurrentTool('geo');
				}}
				className="custom-tool" 
				id="tool-star" 
				src={starIcon} 
				alt="star"
				draggable="false"
			/>
			<img 
				className="custom-tool" 
				id="tool-rectangle" 
				src={rectangleIcon} 
				alt="rectangle"
				draggable="false"
				onClick={() => {
					editor.updateInstanceState(
						{
							stylesForNextShape: {
								...editor.getInstanceState().stylesForNextShape,
								[GeoShapeGeoStyle.id]: "rectangle",
							},
						},
						{ ephemeral: true }
					);
					editor.setStyleForNextShapes(
						DefaultColorStyle, 
						props.currentColor
					);
					editor.setCurrentTool('geo');
				}}
			/>
			{/* <span class="vertical-bar"></span> */}
			<img 
				className="custom-tool" 
				id="tool-reload" 
				src={reloadIcon} 
				alt="reload"
				draggable="false"
				onClick={() => {
					// Regenerate the most recent layout. 
					console.log("Running reload");
					props.setReloadClicked(true);
				}}
			/>	
			{/* <span className="vertical-bar"></span>
			<div className="show-layout-button">
				Show Layout
			</div> */}
		</div>
	)
});

const colorPaletteToHex = {
	"blue": "#2f80ed",
	"orange": "#f76706",
	"green": "#0b9268",
}

function Arrow(props) {
	return <>
		<span>&nbsp;</span>
		<svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
			<path d="M24 18.4667L24 6.00001M24 6.00001L11.5333 6.00001M24 6.00001L7.00002 23" stroke={props.color} stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
		</svg>
		<span>&nbsp;</span>
	</>
}

function Rectangle(props) {
	return <>
		<span>&nbsp;</span>
		<svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
			<path d="M5 3H25C26.1046 3 27 3.89543 27 5V25C27 26.1046 26.1046 27 25 27H5C3.89543 27 3 26.1046 3 25V5C3 3.89543 3.89543 3 5 3Z" stroke={props.color} stroke-width="3"/>
		</svg>
		<span>&nbsp;</span>
	</>
}

function Star(props) {
	return <>
		<span>&nbsp;</span>
		<svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
			<path d="M15 3.53101L19.1119 9.19117C19.3602 9.53294 19.7103 9.78732 20.1121 9.91783L26.7658 12.0794L22.6533 17.7391C22.405 18.0809 22.2713 18.4925 22.2713 18.9149L22.2717 25.911L15.6181 23.7487C15.2164 23.6181 14.7836 23.6181 14.3819 23.7487L7.72831 25.911L7.72868 18.9149C7.7287 18.4925 7.59497 18.0809 7.34665 17.7391L3.23417 12.0794L9.88794 9.91783C10.2897 9.78732 10.6398 9.53294 10.8881 9.19117L15 3.53101Z" stroke={props.color} stroke-width="3"/>
		</svg>
		<span>&nbsp;</span>
	</>
}

function getShapeType(shape) {
	if (shape.type === "arrow") {
		return "arrow";
	} else if (shape.type === "geo") {
		return shape.props.geo;
	} else {
		return "other"
	}
}

// Implements a vertical bar where different backgrounds can be selected. 
const Backgrounds = track((props) => {
	const editor = useEditor();
	const [classNames, updateClassNames] = useState({});
	const loading = props.loading;

	useEffect(() => {
		// Update the classNames 
		const newClassNames = {};
		Object.entries(default_background_data).map(([backgroundKey, backgroundData]) => {
			newClassNames[backgroundKey] = "background-bar-item" + (props.currentBackground === backgroundKey ? " active" : " inactive");
		});
		updateClassNames(newClassNames);
	}, [props]);

	return (
		<div className={loading ? "background-container loading" : "background-container not-loading"}> 
			{
				Object.entries(default_background_data).map(([backgroundKey, backgroundData]) => {
					return <img
						onClick={() => {
							if (props.currentBackground === backgroundKey) {
								return;
							} else {
								// Remove shapes from the editor
								editor.updateShapes([])
								// Reset the background name
								props.updateCurrentBackground(backgroundKey);
							}
						}}
						draggable="false"
						className={classNames[backgroundKey]}
						key={backgroundKey}
						src={backgroundData.background_image}
					>
					</img>
				})
			}
		</div>
	)
})

// Input box
const InputBox = function(props) {
	const editor = useEditor()
	const inputBoxRef = useRef(null);
	const containerRef = props.containerRef;
	const buttonRef = useRef(null);
	// const updateColorIndex = props.updateColorIndex;
	const resetColorIndex = props.resetColorIndex;
	// const currentColor = props.currentColor;
	const [shapeIds, setShapeIds] = useState([]);
	const prevShapeIdsRef = useRef();
	// const prevInputBoxState = useRef();
	const loading = props.loading;
	const setLoading = props.setLoading;
	const [offset, setOffset] = useState(0);
	const [inputBoxHTML, setInputBoxHTML] = useState("");
	// const [addShapeHandlerAdded, setAddShapeHandlerAdded] = useState(false);
	function clearEditorState() {
		// Removes everything from the canvas
		// editor.updateAssets([]);
		editor.deleteAssets(editor.getAssets());
		// Remove shapes 
		for (let shapeId of shapeIds) {
			editor.deleteShapes([shapeId]);
		}
		// Empty the input box 
		setInputBoxHTML("");
		setOffset(0);
		resetColorIndex();
		// Remove the shapes from the state
		setShapeIds([]);
	}

	function convertInstructionToEmoji(instruction) {
		// Converts the given instruction to a format that can be understood by the input box
		// I.e. "Add a dog {'x': 0.2, 'y': 0.3, 'width': 0.5, 'height': 0.5}" to "Add a dog ⭐"
		let textInstruction = "";
		let readingShape = false;
		let shapeString = ""; 
		for (let char of instruction) {
			if (!readingShape) {
				if (char === "{") {
					readingShape = true;
					shapeString = "{";
				} else {
					textInstruction += char;
				}
			} else {
				shapeString += char;
				if (char === "}") {
					readingShape = false;
					// Now detect if the shape is a point or rectangle
					const shape = JSON.parse(shapeString);
					if (shape["width"] === undefined) {
						// Add a star to the instruction
						textInstruction += "⭐";
					} else {
						// Add a rectangle to the instruction
						textInstruction += "🟦";
					}
					// Empty the shape string
					shapeString = "";
				}
			}
		}
	
		return textInstruction;
	}

	function populateDefaultInstruction(currentBackground) {
		const defaultInstruction = default_background_data[currentBackground].default_instruction;
		const defaultInstructionString = convertInstructionToEmoji(defaultInstruction);
		setInputBoxHTML(defaultInstructionString);
		// Add each of the shapes in the instructions to the editor
		let shapeIds = [];
		// Extract the json substrings from the instruction
		const jsonRegex = /\{([^}]+)\}/g;
		// Use match method to find all JSON substrings in the string
		const jsonSubstrings = defaultInstruction.match(jsonRegex);
		if (jsonSubstrings === null) {
			return;
		}
		// Parse each JSON substring and return as an array of JavaScript objects
		const shapes = jsonSubstrings.map(jsonString => JSON.parse(jsonString));
		// Figure out each shape type
		for (let shape of shapes) {
			if (shape["width"] === undefined) {
				// Add a star to the editor
				const newShape = {
					id: createShapeId(),
					type: 'geo',
					x: roundToTwoDigits(parseInt(shape["x"] * imageWidth) + (tldrawWidth - imageWidth)),
					y: roundToTwoDigits(parseInt(shape["y"] * imageHeight) + (tldrawHeight - imageHeight)),
					isLocked: false,
					props: {
						w: roundToTwoDigits(parseInt(imageWidth * 0.05)),
						h: roundToTwoDigits(parseInt(imageHeight * 0.05)),
						geo: "star",
						color: "blue",
						size: "l"
					},
				};
				editor.createShapes([newShape]);
				// Add the shapeid to the shape Ids list
				shapeIds.push(newShape.id);
			} else {
				// Add a rectangle
				const newShape = {
					id: createShapeId(),
					type: 'geo',
					x: roundToTwoDigits(parseInt(shape["x"] * imageWidth) + (tldrawWidth - imageWidth) / 2),
					y: roundToTwoDigits(parseInt(shape["y"] * imageHeight) + (tldrawHeight - imageHeight) / 2),
					isLocked: false,
					props: {
						w: parseInt(shape["width"] * imageWidth),
						h: parseInt(shape["height"] * imageHeight),
						geo: "rectangle",
						color: "blue",
						size: "l"
					},
				}
				editor.createShapes([newShape]);
				// Add the shapeid to the shape Ids list
				shapeIds.push(newShape.id);
			} 
			// Add shape ids to the state
			setShapeIds(shapeIds);
			prevShapeIdsRef.current = shapeIds;
		}
	}

	// Handle figuring out the instruction and calling the backend API.
	function mapInputBoxContentsToInstruction(currentInput, shapeIds){
		// Take the contents of the input box and the current shapes
		// and map them to an instruction to be passed to the backend. 
		let instruction = "";
		let shapeIndex = 0;
		if (shapeIds === undefined || shapeIds.length == 0) {
			return currentInput;
		}
		for (let char of currentInput) {
			if (char === "⭐" || char === "🟦") {
				// Get the shape id
				const shapeId = shapeIds[shapeIndex];
				// Get the most recent shape of that ID from the editor
				const shape = editor.getShape(shapeId);
				// Get the shape specific info from the object
				if (char === "⭐") {
					// Add a star to the instruction
					instruction += JSON.stringify({
						'x': roundToTwoDigits((shape.x - (tldrawWidth - imageWidth) / 2) / imageWidth),
						'y': roundToTwoDigits((shape.y - (tldrawHeight - imageHeight) / 2) / imageHeight),
					});
					shapeIndex += 1;
				} else if (char === "🟦") {
					// Add a rectangle to the instruction
					instruction += JSON.stringify({
						'x': roundToTwoDigits((shape.x - (tldrawWidth - imageWidth) / 2) / imageWidth),
						'y': roundToTwoDigits((shape.y - (tldrawHeight - imageHeight) / 2) / imageHeight),
						'width': roundToTwoDigits(shape.props.w / imageWidth),
						'height': roundToTwoDigits(shape.props.h / imageHeight),
					});
					shapeIndex += 1;
				}
			} else {
				instruction += char;
			}
		}

		return instruction;
	}

	function callImageGenerationAPI(currentBackground, currentLayout, shapeIds, inputBoxContents, reload){
		/*
			This function handles communicating with the backend API. The backend 
			is assumed to be stateless, but does have acess to image files. 

			This API serves two purposes:
			- When a user selects a new background or on load, the API is called to
				get the default image for the background. This is done by sending the 
				default layout json, a background identifier, object -> image mapping 
				and an empty instruction (this tells the backend to not perform editing and
				just run the layout to image conversion (possibly with caching)). The
				backend then returns an image and an unchanged state. 
			- When the user clicks the "Run" button, the API is called to edit the image 
				based on the instruction. This is done by sending the layout json, a background
				identifier, object -> image mapping and the instruction. The backend will return an image
				and a modified layout, and object -> image mapping state. 
		*/
		// Form the message to call the API
		const jsonData = {
			"layout": currentLayout, // The layout from the state
			"background": currentBackground, // The background identifier
			// "object_image_mapping": {}, // The object -> image mapping
			"instruction": mapInputBoxContentsToInstruction(inputBoxContents, shapeIds), // convertInputBoxArrayToInstruction(state["inputBoxArray"], state["shapes"]) // The instruction
			"reload": false ? reload === undefined : reload, // Whether to reload the most recent layout
		}
		console.log("API Call JSON: ", jsonData)
		const assetId = AssetRecordType.createId()
		// Clear the editor state
		clearEditorState();
		// Set to loading screen
		setLoading(true);
		// Append query string to a base URL
		const baseUrl = 'http://127.0.0.1:' + port + '/generate_image';
		console.log(baseUrl)
		return fetch(baseUrl,  {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(jsonData)
			})
			.then(response => response.json())
			.then(data => {
				const base64String = data.image
				const imageString = 'data:image/png;base64,' + base64String;
				//[2]
				editor.createAssets([
					{
						id: assetId,
						type: 'image',
						typeName: 'asset',
						props: {
							name: 'logo192.png',
							src: imageString, // You could also use a base64 encoded string here
							w: imageWidth,
							h: imageHeight,
							mimeType: 'image/png',
							isAnimated: false,
						},
						meta: {},
					},
				])
				//[3]
				editor.createShape({
					type: 'image',
					// Let's center the image in the editor
					x: (tldrawWidth - imageWidth) / 2,
					y: (tldrawHeight - imageHeight) / 2,
					isLocked: true,
					props: {
						assetId,
						w: imageWidth,
						h: imageHeight,
					},
				})
				// Set to no longer loading 
				setLoading(false);
				// Update the layout state
				const layout = data.layout;
				console.log("Edited layout: ", layout);
				props.setState(
					prevState => {
						return {
							...prevState,
							"layout": layout,
						}
					}
				)
			}).catch(error => console.log('Error:', error));
	}

	useEffect(() => {
		// Listen for shape added or removed to component state
		// Figure out if a shape was added or removed based on the difference between the previous and current state
		const added = prevShapeIdsRef.current === undefined || shapeIds.length > prevShapeIdsRef.current.length;
		if (added) {
			// Handle shape add event
			const newShapeIds = shapeIds.filter(shapeId => !prevShapeIdsRef.current.includes(shapeId));
			// Add emojis in order to the input box as spans (at the cursor position)
			for (let shapeId of newShapeIds) {
				const shape = editor.getShape(shapeId);
				const shapeType = getShapeType(shape);
				if (shapeType === "star") {
					// Add a star emoji to the input box
					const text = inputBoxHTML.replace(/&nbsp;/g, ' ');
					setInputBoxHTML(
						text.slice(0, offset) + " ⭐ " + text.slice(offset)
					)
					setOffset(offset + 3);
				} else if (shapeType === "rectangle") {
					// Add a square emoji to the input box
					const text = inputBoxHTML.replace(/&nbsp;/g, ' ');
					setInputBoxHTML(
						text.slice(0, offset) + " 🟦 " + text.slice(offset)
					)
					setOffset(offset + 3);
				}
			}
		}
		// Check for remove event
		const removed = !prevShapeIdsRef.current === undefined && prevShapeIdsRef.current.length > shapeIds.length;
		if (removed) {
			// Handle shape remove event
			console.log("Handling shape remove")
		}
		// Update the ref
		prevShapeIdsRef.current = shapeIds;
	}, [shapeIds]);

	useEffect(() => {
		// Add an event listener for when backspace or delete are pressed and the canvas is in focus
		function handleKeyPressed(event) {
			// Ensure target of event is the canvas and not the input box
			if (event.target !== inputBoxRef.current) {
				// If backspace or delete are pressed when the canvas is in focus
				if (event.key === "Backspace" || event.key === "Delete") {
					// then remove the selected shape (s) from the canvas and input bar/state
					const selectedShapeIds = editor.getSelectedShapeIds();
					editor.deleteShapes(selectedShapeIds);
					// Get the index of the selectedShapeIds in the shapeId array
					const selectedShapeIndices = selectedShapeIds.map(shape => shapeIds.indexOf(shape.id));
					// Now delete each of these selected shapes from the state
					setShapeIds(
						prevState => {
							return prevState.filter(shapeId => !selectedShapeIds.includes(shapeId));
						}
					);
					// Delete their corresponding emoji span's from inside the input box
					let newInnerHTML = "";
					let shapeCount = 0;
					for (let i = 0; i < inputBoxHTML.length; i++) {
						if (inputBoxHTML[i] === "⭐" || inputBoxHTML[i] === "🟦") {
							if (selectedShapeIndices.includes(shapeCount)) {
								// Do nothing
							} else {
								newInnerHTML += inputBoxHTML[i];
							}
							shapeCount += 1;
						} else {
							newInnerHTML += inputBoxHTML[i];
						}
					}
					setInputBoxHTML(newInnerHTML);
				}
			} else if (event.target == inputBoxRef.current) {
				// If backspace or delete are pressed when the input box is in focus
				if (event.key === "Backspace" || event.key === "Delete") {
					// TODO 
				}
			}
		}

		// Restore the offset
		if (inputBoxRef.current.childNodes.length > 0) {
			const selection = window.getSelection();
			const range = document.createRange();
			range.setStart(inputBoxRef.current.firstChild, offset);
			range.setEnd(inputBoxRef.current.firstChild, offset);
			range.collapse(true);
			selection.removeAllRanges();
			selection.addRange(range);
		}
		// Add the event listeners
		containerRef.current.addEventListener("keydown", handleKeyPressed);
		function callAPIClosure() {
			callImageGenerationAPI(props.currentBackground, props.layout, shapeIds, inputBoxHTML);
		}
		buttonRef.current.addEventListener("click", callAPIClosure);

		return () => {
			// Remove the event listener
			if (containerRef.current) {
				containerRef.current.removeEventListener("keydown", handleKeyPressed);
			}
			if (buttonRef.current) {
				buttonRef.current.removeEventListener("click", callAPIClosure);
			}
		}
	}, [shapeIds, inputBoxHTML, offset, props.currentBackground]);

	useEffect(() => {
		// Clear the editor state
		clearEditorState();
		// Add the background layout to the editor
		// Now call the image generation API
		callImageGenerationAPI(
			props.currentBackground,
			props.layout,
			[],
			""
		).then(() => {
			// Populate the input box with the default instruction
			populateDefaultInstruction(props.currentBackground);
		})
	}, [props.currentBackground]);

	useEffect(() => {
		// Listen for added shapes and then add it to the component state
		editor.store.listen((entry) => {
			const added = entry.changes.added;
			// Get all of the Geo shapes
			let geoShapes = Object.values(added)
				.filter(shape => shape.type === "geo")

			for (let shape of geoShapes) {
				// Add the shape to the object state
				setShapeIds(
					prevState => {
						return [
							...prevState,
							shape.id
						]
					}
				);
			}
		})
	}, []);

	useEffect(() => {
		// Loading screen
	}, [loading]);

	useEffect(() => {
		// If the reload button is clicked, then call the image generation API
		props.setReloadClicked(false);
		console.log("Running reload operation")
		if (props.reloadClicked) {
			callImageGenerationAPI(
				props.currentBackground,
				props.layout,
				shapeIds,
				inputBoxHTML,
				true
			)
		}
	}, [props.reloadClicked]);

	function handleSelection() {
		const selection = window.getSelection();
		if (selection.rangeCount > 0) {
			const range = selection.getRangeAt(0);
			setOffset(range.startOffset);
		}
	}

	function handleContentChange() {
		setInputBoxHTML(inputBoxRef.current.innerHTML);
		setOffset(window.getSelection().getRangeAt(0).startOffset);
	};

	return (
		<div
			className="input-box-container"
			onKeyDown={(event) => {
					// Detect enter key
					if (event.key === "Enter") {
						console.log("Enter key pressed")
						// Call the image generation API
						callImageGenerationAPI(
							props.currentBackground,
							props.layout,
							shapeIds,
							inputBoxHTML
						);
						event.preventDefault();
					}
				}
			}
		>
			<div 
				className={loading ? "input-box loading" : "input-box not-loading"}
				type="text"
				data-placeholder="Write a prompt"
				contentEditable="true"
				ref={inputBoxRef}
				onInput={handleContentChange}
				onSelect={handleSelection}
				dangerouslySetInnerHTML={{__html: inputBoxHTML}}
			/>
			<div 
				className={loading ? "input-box-button loading" : "input-box-button not-loading"}
				ref={buttonRef}
			>
				Run
			</div>
		</div>
	);
}

function App(){
	// Create a reference to input box
	const editorWrapperRef = createRef();
	// Setup state that stores the information for the input box
	const [state, setState] = useState({
		currentColorIndex: 0,
		currentBackground: "park",
		layout: default_background_data["park"].default_layout,
	})

	const [loading, setLoading] = useState(false);
	const [reloadClicked, setReloadClicked] = useState(false);

	const myOverrides = {
		tools(editor, tools) {
			tools.hand = {
				id: 'hand',
				label: 'tool.hand',
				icon: 'tool-hand',
				kbd: 'h',
				readonlyOk: true,
				onSelect(source) {
					// Do nothing
				},
			}

			return tools;
		}
	}

	const updateColorIndex = () => {
		setState(
			prevState => {
				return {
					...prevState,
					currentColorIndex: (prevState.currentColorIndex + 1) % colorPalette.length
				};
			}
		);
	};

	const resetColorIndex = () => {
		setState(
			prevState => {
				return {
					...prevState,
					currentColorIndex: 0
				};
			}
		);
	}

	const updateCurrentBackground = (backgroundKey) => {
		// Add the new background image to the editor, and add the default input box. 
		setState(
			prevState => {
				return {
					...prevState,
					currentBackground: backgroundKey, 
					layout: default_background_data[backgroundKey].default_layout,
				};
			}
		);
	}

	return (
		<div className="App">
			<div 
				className="tldraw-editor"
				ref={editorWrapperRef}
			>
				<div className={loading ? "loading-overlay-loading" : "loading-overlay-not-loading"}>
					<img src={loadingGIF} className="loading-gif" alt="loading" draggable="false"></img>
				</div> 
				<Tldraw 
					hideUi
					overrides={myOverrides}
					onMount={(editor) => {
						editor.updateInstanceState({canMoveCamera: false})
						editor.user.updateUserPreferences({ edgeScrollSpeed: 0.0 })
						// editor.on('event', (event) => {handleEvent(event)})
					}}
				>
					<div className="custom-layout">
						<div className="left-container">
							<Backgrounds
								currentBackground={state.currentBackground}
								updateCurrentBackground={updateCurrentBackground}
								loading={loading}
							/>
						</div>
						<div className="right-container">
							<Toolbar
								currentColor={colorPalette[state.currentColorIndex]}
								loading={loading}	
								setReloadClicked={setReloadClicked}
							/>
							<InputBox
								updateColorIndex={updateColorIndex}
								resetColorIndex={resetColorIndex}
								currentColor={colorPalette[state.currentColorIndex]}
								containerRef={editorWrapperRef}
								currentBackground={state.currentBackground}
								layout={state.layout}
								loading={loading}
								setLoading={setLoading}
								setState={setState}
								reloadClicked={reloadClicked}
								setReloadClicked={setReloadClicked}
							/>
						</div>
					</div>
				</Tldraw>
			</div>
		</div>
	);
}

export default App;