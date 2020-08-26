# Connect Security Requirements Scan
Generated for **{{ results.name }}** ({{ results.key }}) hosted at: [{{ results.base_url }}]({{ results.base_url }}) on **{{ today }}**

**{{ results.name }}** was evaluated against the [Security Requirements for Cloud Applications](https://developer.atlassian.com/platform/marketplace/security-requirements/). For additional information on requirements, visit the [addditional information guide on security requirements](https://developer.atlassian.com/platform/marketplace/security-requirements-more-info/).

*Please note, this automated scan does a best-effort attempt at evaluating your cloud app. If you believe there is an error in a finding, reach out to us at: [https://go.atlassian.com/connect-sec-test](https://go.atlassian.com/connect-sec-test)*

*Raw scan output is located in the Appendix at the end of the report.*

## Scan Results

{% for req in results.requirements %}
### Requirement {{ req }} - {{ titles[req] }}

Passed: {% if constants.NO_SCAN_INFO[req] %} **No Scan Performed** {% else %} **{{ results.requirements[req]['passed'] }}** {% endif %}

Description:

* {% if constants.NO_SCAN_INFO[req] %} {{ constants.NO_SCAN_INFO[req] }} {% else %} {{ results.requirements[req]['description'] | join('\n\n* ') }} {% endif %}

Proof:
{% if results.requirements[req]['proof'] %}
* {{ results.requirements[req]['proof'] | join('\n\n* ') }}
{% elif constants.NO_SCAN_INFO[req] %}
* {{ constants.NO_SCAN_PROOF }}
{% else %}
* {{ constants.NO_PROOF }}
{% endif %}

---
{% endfor %}

## Appendix
### SSL/TLS Scan Raw Output
Obtained via the [Qualys SSL Labs API](https://www.ssllabs.com/ssltest/)

```
{{ results['tls_scan_raw'] }}
```

### Connect App Descriptor Evaluation
Obtained via the App Descriptor located at: [{{ results['app_descriptor_url'] }}]({{ results['app_descriptor_url'] }})

```
{{ results['descriptor_scan_raw'] }}
```