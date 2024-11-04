import xml.etree.ElementTree as ET

class XML_converter:
    def create_root(self, root_name: str):
        root = ET.Element(root_name)
        
        return root

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
            attribute = ET.Element("attribute")
            ET.SubElement(attribute, "key").text = key
            ET.SubElement(attribute, "value").text = value
            result.append(attribute)
        
        return result
    
    def create_rect(self, anno: dict):
        annotation = ET.Element("rect")
        
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
        annotation = ET.Element("polygon")
        
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
        annotation = ET.Element("point")
        
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
        annotation = ET.Element("line")
        
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
        annotation = ET.Element("cuboid")
        
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
        annotation = ET.Element("tag")
        
        ET.SubElement(annotation, "toolName").text = "tagTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        
        ET.SubElement(result, "id").text = anno.get("id", "")
        
        values = ET.Element("values")
        for key, value in anno.get("value", {}).items():
            ET.SubElement(values, key).text = ", ".join(value) if value else ""
        
            
        result.append(values)
        annotation.append(result)
        
        return annotation
    
    def create_text(self, anno: dict):
        annotation = ET.Element("text")
        
        ET.SubElement(annotation, "toolName").text = "textTool"
        
        result = ET.Element("result")
        
        ET.SubElement(result, "order").text = str(anno.get("order", 0))
        ET.SubElement(result, "id").text = anno.get("id", "")
        
        values = ET.Element("values")
        for key, value in anno.get("value", {}).items():
            ET.SubElement(values, key).text = value
        
        result.append(values)
        annotation.append(result)
        
        return annotation
  