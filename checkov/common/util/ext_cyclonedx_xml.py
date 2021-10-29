from cyclonedx.output.xml import Xml
from xml.etree import ElementTree


class ExtXml(Xml):

    def output_as_string(self) -> str:
        bom = self._get_bom_root_element()

        if self.bom_supports_metadata():
            bom = self._add_metadata(bom=bom)

        if self.get_bom().has_vulnerabilities():
            ElementTree.register_namespace('v', Xml.get_vulnerabilities_namespace())

        components = ElementTree.SubElement(bom, 'components')

        for component in self.get_bom().get_components():
            component_element = self._get_component_as_xml_element(component=component)
            components.append(component_element)
            if component.has_vulnerabilities() and self.component_supports_bom_ref():
                # Vulnerabilities are only possible when bom-ref is supported by the main CycloneDX schema version
                vulnerabilities = ElementTree.SubElement(component_element, 'v:vulnerabilities')
                for vulnerability in component.get_vulnerabilities():
                    vulnerabilities.append(self._get_vulnerability_as_xml_element(bom_ref=component.get_purl() +
                                                                                          vulnerability.get_id(),
                                                                                  vulnerability=vulnerability))

        return Xml.XML_VERSION_DECLARATION + ElementTree.tostring(bom, 'unicode')
