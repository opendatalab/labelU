import json
import os
from PIL import Image
from typing import List
from tfrecord import example_pb2
from labelu.internal.common.config import settings

class TF_record_converter:
    def __init__(self):
        self.label_map = {}
        
    def _get_label_id(self, label: str):
        if label not in self.label_map:
            self.label_map[label] = len(self.label_map) + 1
            
        return self.label_map[label]
        
    def create_tf_examples(self, sample_results: List[dict], config: dict):
        examples = []
        label_text_dict = {}
        
        for tool in config.get("tools", []):
            label_text_dict[tool.get("tool")] = { attr.get("value"): attr.get("key") for attr in tool.get("config", {}).get("attributes", [])}
        
        common_attributes = { attr.get("value"): attr.get("key") for attr in config.get("attributes", [])}
        
        def get_label(_tool: str, _input_label: str):
            _label = label_text_dict.get(_tool, {}).get(_input_label, "")
            
            if not _label:
                _label = common_attributes.get(_input_label, "")
                
            return _label
        
        classes_text = []
        classes = []
        
        for sample in sample_results:
            data = json.loads(sample.get("data"))
            file = sample.get("file", {})
            
            # skip invalid data
            annotated_result = json.loads(data.get("result"))
            if sample.get("state") == "SKIPPED" or not annotated_result:
                continue
            
            image_width = annotated_result.get("width", 0)
            image_height = annotated_result.get("height", 0)
            rotate = annotated_result.get("rotate", 0)
            
            _, file_extension = os.path.splitext(file.get("filename", ""))
            
            file_full_path = settings.MEDIA_ROOT.joinpath(file.get("path").lstrip("/"))
            
            with Image.open(file_full_path) as img:
                if rotate:
                    img = img.rotate(rotate)

                image_width, image_height = img.size
                encoded_image_data = img.tobytes()
            
            xmins = []
            xmaxs = []
            ymins = []
            ymaxs = []
            line_x = []
            line_y = []
            segmentation = []
            keypoints_x = []
            keypoints_y = []
            keypoints_visibility = []
            cuboid_front = []
            cuboid_back = []
            tags = []
            texts = []
            
            base_info = {
                "image/width": self._int64_feature(image_width),
                "image/height": self._int64_feature(image_height),
                "image/filename": self._bytes_feature(file['filename'].encode('utf8')),
                "image/source_id": self._bytes_feature(file['filename'].encode('utf8')),
                "image/encoded": self._bytes_feature(encoded_image_data),
                "image/format": self._bytes_feature(file_extension.encode('utf8')),
            }

            for tool in annotated_result.copy().keys():
                tool_results = annotated_result.pop(tool)
                if tool == "rectTool":
                    for tool_result in tool_results.get("result", []):
                        label_text = get_label(tool, tool_result.get("label", ""))
                        classes_text.append(label_text.encode('utf8'))
                        classes.append(self._get_label_id(label_text))
                        xmins.append(tool_result.get("x", 0) / image_width)
                        xmaxs.append((tool_result.get("x", 0) + tool_result.get("width", 0)) / image_width)
                        ymins.append(tool_result.get("y", 0) / image_height)
                        ymaxs.append((tool_result.get("y", 0) + tool_result.get("height", 0)) / image_height)

                    base_info.update(
                        {
                            "image/object/bbox/xmin": self._float_list_feature(xmins),
                            "image/object/bbox/xmax": self._float_list_feature(xmaxs),
                            "image/object/bbox/ymin": self._float_list_feature(ymins),
                            "image/object/bbox/ymax": self._float_list_feature(ymaxs),
                        }
                    )
                if tool == "lineTool":
                    for tool_result in tool_results.get("result", []):
                        points = tool_result.get("points", [])
                        
                        label_text = get_label(tool, tool_result.get("label", ""))
                        classes.append(label_text.encode('utf8'))
                        classes.append(self._get_label_id(label_text))
                        
                        for point in points:
                            line_x.append(point.get("x", 0) / image_width)
                            line_y.append(point.get("y", 0) / image_height)

                    base_info.update(
                        {
                            "image/object/line/x": self._float_list_feature(line_x),
                            "image/object/line/y": self._float_list_feature(line_y),
                        }
                    )
                    
                if tool == "polygonTool":
                    for tool_result in tool_results.get("result", []):
                        points = tool_result.get("points", [])
                        segmentation = []
                        for point in points:
                            segmentation.append(point.get("x", 0) / image_width)
                            segmentation.append(point.get("y", 0) / image_height)
                        label = tool_result.get("label", "")
                        classes_text.append(label.encode('utf8'))
                        classes.append(self._get_label_id(label))
                        
                    base_info.update(
                        {
                            "image/object/segmentation": self._float_list_feature(segmentation),
                        }
                    )
                
                if tool == "pointTool":
                    for tool_result in tool_results.get("result", []):
                        points = tool_result.get("points", [])
                        for point in points:
                            keypoints_x.append(point.get("x", 0) / image_width)
                            keypoints_y.append(point.get("y", 0) / image_height)
                            # TODO: visibility
                            keypoints_visibility.append(2)
                            
                        label = tool_result.get("label", "")
                        classes_text.append(label.encode('utf8'))
                        classes.append(self._get_label_id(label))
                        
                    base_info.update(
                        {
                            "image/object/keypoints/x": self._float_list_feature(keypoints_x),
                            "image/object/keypoints/y": self._float_list_feature(keypoints_y),
                            "image/object/keypoints/visibility": self._int64_feature(keypoints_visibility),
                        }
                    )
                        
                if tool == "cuboidTool":
                    for tool_result in tool_results.get("result", []):
                        front = tool_result.get("front", {})
                        back = tool_result.get("back", {})
                        for key in ["tl", "tr", "br", "bl"]:
                            cuboid_front.append(front.get(key, {}).get("x", 0) / image_width)
                            cuboid_front.append(front.get(key, {}).get("y", 0) / image_height)
                            cuboid_back.append(back.get(key, {}).get("x", 0) / image_width)
                            cuboid_back.append(back.get(key, {}).get("y", 0) / image_height)
                        label = tool_result.get("label", "")
                        classes_text.append(label.encode('utf8'))
                        classes.append(self._get_label_id(label))
                        
                    base_info.update(
                        {
                            "image/object/cuboid/front": self._float_list_feature(cuboid_front),
                            "image/object/cuboid/back": self._float_list_feature(cuboid_back),
                        }
                    )
                
                if tool == "tagTool":
                    for tool_result in tool_results.get("result", []):
                        for _, tag in tool_result.get("value", {}).items():
                            for value in tag:
                                tags.append(value.encode('utf8'))
                    
                    base_info.update(
                        {
                            "image/object/tag": self._bytes_feature(tags),
                        }
                    )

                if tool == "textTool":
                    for tool_result in tool_results.get("result", []):
                        for _, text in tool_result.get("value", {}).items():
                            texts.append(text.encode('utf8'))
                            
                    base_info.update(
                        {
                            "image/object/text": self._bytes_feature(texts),
                        }
                    )
                    
            base_info.update(
                {
                    "image/object/class/text": self._bytes_feature(classes_text),
                    "image/object/class/label": self._int64_feature(classes),
                }
            )
            
            examples.append(example_pb2.Example(features=example_pb2.Features(feature=base_info)))
        
        return examples            
        
    
    def _bytes_feature(self, value: bytes | List[bytes]):
        return example_pb2.Feature(bytes_list=example_pb2.BytesList(value=[value] if isinstance(value, bytes) else value))

    def _float_list_feature(self, value: List[float]):
        return example_pb2.Feature(float_list=example_pb2.FloatList(value=value))

    def _int64_feature(self, value: int | List[int]):
        return example_pb2.Feature(int64_list=example_pb2.Int64List(value=[value] if isinstance(value, int) else value))
