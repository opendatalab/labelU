"""Change tool config format

Revision ID: 363f9eea797e
Revises: 9d5da133bbe4
Create Date: 2023-04-03 15:08:12.508189

"""
from alembic import op
from alembic import context
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from pydantic import BaseModel
from typing import Optional, List
from random import choice

# revision identifiers, used by Alembic.
revision = "363f9eea797e"
down_revision = "9d5da133bbe4"
branch_labels = None
depends_on = None

# produce a set of mappings from this MetaData
Base = automap_base()

# define the tool config default value
defaultColors = [
    "#fc5b50",
    "#FC7A42",
    "#FFB300",
    "#3BC141",
    "#50AAF2",
    "#506AFF",
    "#8D64FF",
    "#D55EEA",
    "#F974A4",
    "#DE8B3E",
    "#FF5C97",
    "#FFCC4A",
    "#F1F462",
    "#ABFF7E",
    "#52CEDD",
    "#5AB4DB",
    "#99D5F0",
    "#958FEC",
    "#AD6DDB",
    "#B77259",
]

# define the new tool config model
class NewAttribute(BaseModel):
    color: str
    key: str
    value: str


class NewOption(BaseModel):
    key: str
    value: str
    type: Optional[str] 
    maxLength: Optional[int] 
    stringType: Optional[str] 
    defaultValue: Optional[str] 
    regexp: Optional[str] 
    isDefault: Optional[bool] 


class NewConfigAttribute(BaseModel):
    color: Optional[str] 
    key: str
    value: Optional[str] 
    options: Optional[List[NewOption]] 
    type: Optional[str] 
    stringType: Optional[str] 
    label: Optional[str] 
    required: Optional[bool] 
    defaultValue: Optional[str] 
    maxLength: Optional[int] 


class NewConfig(BaseModel):
    isShowCursor: Optional[bool] 
    showConfirm: Optional[bool] 
    skipWhileNoDependencies: Optional[bool] 
    drawOutsideTarget: Optional[bool] 
    copyBackwardResult: Optional[bool] 
    minWidth: Optional[int] 
    attributeConfigurable: Optional[bool] 
    textConfigurable: Optional[bool] 
    attributes: Optional[List[NewConfigAttribute]]
    minHeight: Optional[int] 


class NewTool(BaseModel):
    tool: str
    config: NewConfig


class NewToolConfig(BaseModel):
    attributes: Optional[List[NewAttribute]] 
    tools: Optional[List[NewTool]] 
    commonAttributeConfigurable: Optional[bool] 


# define the old tool config model
class OldAttributeItem(BaseModel):
    key: str
    value: str


class OldAttributeListItem(BaseModel):
    key: str
    value: str


class OldConfig(BaseModel):
    isShowCursor: Optional[bool]
    showConfirm: Optional[bool]
    skipWhileNoDependencies: Optional[bool]
    drawOutsideTarget: Optional[bool]
    copyBackwardResult: Optional[bool]
    minWidth: Optional[int]
    attributeConfigurable: Optional[bool]
    textConfigurable: Optional[bool]
    textCheckType: Optional[int]
    customFormat: Optional[str]
    attributeList: Optional[List[OldAttributeListItem]]
    minHeight: Optional[int]


class OldTool(BaseModel):
    tool: Optional[str]
    config: Optional[OldConfig] 


class OldSubSelectedItem(BaseModel):
    key: Optional[str]
    value: Optional[str]
    isDefault: Optional[bool] 
    isMulti: Optional[bool] 


class OldTagListItem(BaseModel):
    key: Optional[str]
    value: Optional[str]
    isMulti: Optional[bool]
    subSelected:  Optional[List[OldSubSelectedItem]]


class OldTextConfigItem(BaseModel):
    label:  Optional[str]
    key:  Optional[str]
    required:  Optional[bool]
    default:  Optional[str]
    maxLength:  Optional[int]


class OldToolConfig(BaseModel):
    attribute: Optional[List[OldAttributeItem]] 
    tools: Optional[List[OldTool]] 
    commonAttributeConfigurable: Optional[bool] 
    tagList: Optional[List[OldTagListItem]] 
    textConfig: Optional[List[OldTextConfigItem]] 

    def to_new(self) -> NewToolConfig:

        new_tool_config = NewToolConfig()

        # attribute
        if self.attribute:

            new_tool_config.attributes = [
                NewAttribute(color=choice(defaultColors), **attribute.dict())
                for attribute in self.attribute
            ]

        # tools
        if self.tools:

            new_tool_config.tools = [
                NewTool(
                    tool=tool.tool,
                    config=NewConfig(
                        isShowCursor=tool.config.isShowCursor,
                        showConfirm=tool.config.showConfirm,
                        skipWhileNoDependencies=tool.config.skipWhileNoDependencies,
                        drawOutsideTarget=tool.config.drawOutsideTarget,
                        copyBackwardResult=tool.config.copyBackwardResult,
                        minWidth=tool.config.minWidth,
                        attributeConfigurable=tool.config.attributeConfigurable,
                        textConfigurable=tool.config.textConfigurable,
                        minHeight=tool.config.minHeight,
                        attributes=[
                            NewConfigAttribute(
                                color=choice(defaultColors),
                                options=[
                                    NewOption(
                                        key="文本属性-1",
                                        value="text-attribute-1",
                                        type="string",
                                        maxLength=1000,
                                        stringType="regexp",
                                        defaultValue="",
                                        regexp=tool.config.customFormat,
                                    )
                                ]
                                if tool.config.textCheckType == 4
                                else None,
                                **attribute.dict(),
                            )
                            for attribute in tool.config.attributeList
                        ] if tool.config.attributeList else None,
                    ),
                )
                for tool in self.tools
            ]

        # tagList
        if self.tagList:

            for index, tool in enumerate(new_tool_config.tools):

                if tool.tool == "tagTool":

                    new_tool_config.tools[index] = NewTool(
                        tool="tagTool",
                        config=NewConfig(
                            attributes=[
                                NewConfigAttribute(
                                    key=tag.key,
                                    value=tag.value,
                                    type="array" if tag.isMulti else "enum",
                                    options=[
                                        NewOption(
                                            key=subSelected.key,
                                            value=subSelected.value,
                                            isDefault=subSelected.isDefault
                                            if subSelected.isDefault != None
                                            else None,
                                        )
                                        for subSelected in tag.subSelected
                                    ],
                                )
                                for tag in self.tagList
                            ],
                        ),
                    )

                    break

        # textConfig
        if self.textConfig:

            for index, tool in enumerate(new_tool_config.tools):

                if tool.tool == "textTool":

                    new_tool_config.tools[index] = NewTool(
                        tool="textTool",
                        config=NewConfig(
                            attributes=[
                                NewConfigAttribute(
                                    type="string",
                                    stringType="text",
                                    label=attribute_item.label,
                                    key=attribute_item.key,
                                    required=attribute_item.required,
                                    defaultValue=attribute_item.default,
                                    maxLength=attribute_item.maxLength,
                                )
                                for attribute_item in self.textConfig
                            ]
                        ),
                    )

                    break

        # commonAttributeConfigurable
        new_tool_config.commonAttributeConfigurable = self.commonAttributeConfigurable

        return new_tool_config


def upgrade() -> None:

    # get the current connection
    bind = op.get_bind()
    # Reflect ORM models from the database
    Base.prepare(autoload_with=bind, reflect=True)
    task = Base.classes.task
    # make a session
    Session = sessionmaker(bind=bind)
    session = Session()

    # replace the key with value in a transaction
    with context.begin_transaction():
        task_items = session.execute(
            'SELECT id, config FROM task WHERE config IS NOT NULL AND config != ""'
        )

        for task_item in task_items:
            task_id = task_item[0]
            old_tool_config = OldToolConfig.parse_raw(task_item[1])
            new_tool_config = old_tool_config.to_new()
            session.execute(
                update(task)
                .where(task.id == task_id)
                .values(config=new_tool_config.json(exclude_none=True, ensure_ascii=False))
            )


def downgrade() -> None:
    pass
