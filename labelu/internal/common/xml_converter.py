import xml.etree.ElementTree as ET
from labelu.internal.common.config import settings

class XML_converter:
    def create_pascal_voc_xml(self, config: dict, file: dict, sample_result: dict):
        annotation = ET.Element("annotation")
        
        folder = ET.SubElement(annotation, "folder")
        folder.text = str(settings.MEDIA_ROOT)
        
        filename_elem = ET.SubElement(annotation, "filename")
        filename_elem.text = file.get("filename", "")
        
        path_elem = ET.SubElement(annotation, "path")
        path_elem.text = file.get("path")
        
        image_width = sample_result.get("width", 0)
        image_height = sample_result.get("height", 0)
        
        size_elem = ET.SubElement(annotation, "size")
        width = ET.SubElement(size_elem, "width")
        width.text = str(image_width)
        height = ET.SubElement(size_elem, "height")
        height.text = str(image_height)
        depth = ET.SubElement(size_elem, "depth")
        depth.text = "3"
        rotate = ET.SubElement(size_elem, "rotate")
        rotate.text = str(sample_result.get("rotate", 0))
        
        label_text_dict = {}
        
        for tool in config.get("tools", []):
            label_text_dict[tool.get("tool")] = { attr.get("value"): attr.get("key") for attr in tool.get("config", {}).get("attributes", [])}
        
        common_attributes = { attr.get("value"): attr.get("key") for attr in config.get("attributes", [])}
        
        def get_label(_tool: str, _input_label: str):
            _label = label_text_dict.get(_tool, {}).get(_input_label, "")
            
            if not _label:
                _label = common_attributes.get(_input_label, "")
                
            return _label
        
        for tool in sample_result.copy().keys():
            tool_results = sample_result.pop(tool)
            
            if tool == "rectTool":
                for tool_result in tool_results.get("result", []):
                    
                    obj_elem = ET.SubElement(annotation, "object")
                    name = ET.SubElement(obj_elem, "name")
                    name.text = get_label(tool, tool_result.get("label", ""))
                    # get value from attributes
                    truncated = ET.SubElement(obj_elem, "truncated")
                    truncated_value = tool_result.get("attributes", {}).get("truncated", [0])
                    truncated.text = str(truncated_value[0])
                    difficult = ET.SubElement(obj_elem, "difficult")
                    difficult_value = tool_result.get("attributes", {}).get("difficult", [0])
                    difficult.text = str(difficult_value[0])

                    bndbox = ET.SubElement(obj_elem, "bndbox")
                    xmin = ET.SubElement(bndbox, "xmin")
                    xmin_value = tool_result.get("x", 0)
                    xmin.text = str(xmin_value)
                    ymin = ET.SubElement(bndbox, "ymin")
                    ymin_value = tool_result.get("y", 0)
                    ymin.text = str(ymin_value)
                    xmax = ET.SubElement(bndbox, "xmax")
                    xmax.text = str(xmin_value + tool_result.get("width", 0))
                    ymax = ET.SubElement(bndbox, "ymax")
                    ymax.text = str(ymin_value + tool_result.get("height", 0))
                    
        
        return annotation

    def convert_tool_results(self, tool_name, tool_results):
        annotations = []
        for tool_result in tool_results.get("result", []):
            if tool_name == 'rectTool':
                annotation = self.create_rect(tool_result)
            elif tool_name == 'polygonTool':
                annotation = self.create_polygon(tool_result)
            elif tool_name == 'pointTool':
                annotation = self.create_point(tool_result)
            elif tool_name == 'lineTool':
                annotation = self.create_line(tool_result)
            elif tool_name == 'cuboidTool':
                annotation = self.create_cuboid(tool_result)
            elif tool_name == 'tagTool':
                annotation = self.create_tag(tool_result)
            elif tool_name == 'textTool':
                annotation = self.create_text(tool_result)
            else:
                continue
            annotations.append(annotation)
        return annotations

    def create_attributes(self, attributes: dict):
        result = ET.Element("attributes")
        
        for key, value in attributes.items():
            attribute = ET.SubElement(result, "attribute")
            ET.SubElement(attribute, "key").text = key
            ET.SubElement(attribute, "value").text = value if isinstance(value, str) else ", ".join(value)
        
        return result
    
    def create_rect(self, anno: dict):
        annotation = ET.Element("object")
        
        ET.SubElement(annotation, "toolName").text = "rectTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "x").text = str(anno.get("x", 0))
        ET.SubElement(result, "y").text = str(anno.get("y", 0))
        ET.SubElement(result, "width").text = str(anno.get("width", 0))
        ET.SubElement(result, "height").text = str(anno.get("height", 0))
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        
        result.append(self.create_attributes(anno.get("attributes", {})))
        
        annotation.append(result)
        
        return annotation
    
    def create_polygon(self, anno: dict):
        annotation = ET.Element("object")
        
        ET.SubElement(annotation, "toolName").text = "polygonTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "type").text = str(anno.get("type", "line"))
        
        points = ET.Element("points")
        for point in anno.get("points", []):
            p = ET.Element("point")
            
            ET.SubElement(p, "x").text = str(point.get("x", 0))
            ET.SubElement(p, "y").text = str(point.get("y", 0))
            
            points.append(p)
        
        if anno.get("controlPoints"):
            control_points = ET.Element("controlPoints")
            
            for cp in anno.get("controlPoints", []):
                item = ET.Element("controlPoint")
                
                ET.SubElement(item, "x").text = str(cp.get("x", 0))
                ET.SubElement(item, "y").text = str(cp.get("y", 0))
                
                control_points.append(item)
                
            result.append(control_points)
        
        result.append(self.create_attributes(anno.get("attributes", {})))
        result.append(points)
        annotation.append(result)
        
        return annotation
    
    def create_point(self, anno: dict):
        annotation = ET.Element("object")
        
        ET.SubElement(annotation, "toolName").text = "pointTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "x").text = str(anno.get("x", 0))
        ET.SubElement(result, "y").text = str(anno.get("y", 0))
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        
        result.append(self.create_attributes(anno.get("attributes", {})))
        annotation.append(result)
        
        return annotation
    
    def create_line(self, anno: dict):
        annotation = ET.Element("object")
        
        ET.SubElement(annotation, "toolName").text = "lineTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "label").text = anno.get("label", "")
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "type").text = str(anno.get("type", "line"))
        
        points = ET.Element("points")
        for point in anno.get("points", []):
            p = ET.Element("point")
            
            ET.SubElement(p, "x").text = str(point.get("x", 0))
            ET.SubElement(p, "y").text = str(point.get("y", 0))
            
            points.append(p)
        
        if anno.get("controlPoints"):
            control_points = ET.Element("controlPoints")
            
            for cp in anno.get("controlPoints", []):
                item = ET.Element("controlPoint")
                
                ET.SubElement(item, "x").text = str(cp.get("x", 0))
                ET.SubElement(item, "y").text = str(cp.get("y", 0))
                
                control_points.append(item)
                
            result.append(control_points)
            
        result.append(self.create_attributes(anno.get("attributes", {})))
        result.append(points)
        annotation.append(result)
        
        return annotation
    
    def create_cuboid(self, anno: dict):
        annotation = ET.Element("object")
        
        ET.SubElement(annotation, "toolName").text = "cuboidTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "label").text = str(anno.get("label", ""))
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "direction").text = str(anno.get("direction", "front"))
        
        front = ET.Element("front")
        
        for pos, point in anno.get("front", {}).items():
            position = ET.Element(pos)
            ET.SubElement(position, "x").text = str(point.get("x", 0))
            ET.SubElement(position, "y").text = str(point.get("y", 0))
            front.append(position)
        
        back = ET.Element("back")
        for pos, point in anno.get("back", {}).items():
            position = ET.Element(pos)
            ET.SubElement(position, "x").text = str(point.get("x", 0))
            ET.SubElement(position, "y").text = str(point.get("y", 0))
            back.append(position)
            
        result.append(self.create_attributes(anno.get("attributes", {})))
        result.append(front)
        result.append(back)
        
        annotation.append(result)
        
        return annotation
    
    def create_tag(self, anno: dict):
        annotation = ET.Element("object")
        result = ET.SubElement(annotation, "result")
        ET.SubElement(annotation, "toolName").text = "tagTool"
        
        
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        
        ET.SubElement(result, "id").text = anno.get("id", "")
        
        values = ET.SubElement(result, "values")
        
        for key, value in anno.get("value", {}).items():
            ET.SubElement(values, key).text = ", ".join(value) if value else ""
        
        return annotation
    
    def create_text(self, anno: dict):
        annotation = ET.Element("object")
        
        result = ET.SubElement(annotation, "result")
        ET.SubElement(annotation, "toolName").text = "textTool"
        
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "id").text = anno.get("id", "")
        
        values = ET.SubElement(result, "values")
        
        for key, value in anno.get("value", {}).items():
            ET.SubElement(values, key).text = value
        
        return annotation
  