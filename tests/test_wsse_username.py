import os

import pytest
import requests_mock
from freezegun import freeze_time

from tests.utils import assert_nodes_equal, load_xml
from zeep import client
from zeep.wsse.username import UsernameToken


@pytest.mark.requests
def test_integration():
    client_obj = client.Client(
        'tests/wsdl_files/soap.wsdl',
        wsse=UsernameToken('username', 'password'))

    response = """
    <?xml version="1.0"?>
    <soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:stoc="http://example.com/stockquote.xsd">
       <soapenv:Header/>
       <soapenv:Body>
          <stoc:TradePrice>
             <price>120.123</price>
          </stoc:TradePrice>
       </soapenv:Body>
    </soapenv:Envelope>
    """.strip()

    with requests_mock.mock() as m:
        m.post('http://example.com/stockquote', text=response)
        result = client_obj.service.GetLastTradePrice('foobar')
        assert result == 120.123


def test_password_text():
    envelope = load_xml("""
        <soap-env:Envelope
            xmlns:ns0="http://example.com/stockquote.xsd"
            xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
            xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        >
          <soap-env:Body>
            <ns0:TradePriceRequest>
              <tickerSymbol>foobar</tickerSymbol>
              <ns0:country/>
            </ns0:TradePriceRequest>
          </soap-env:Body>
        </soap-env:Envelope>
    """)

    token = UsernameToken('michael', 'geheim')
    envelope, headers = token.sign(envelope, {})
    expected = """
        <soap-env:Envelope
            xmlns:ns0="http://example.com/stockquote.xsd"
            xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
            xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
          <soap-env:Header>
            <ns0:Security xmlns:ns0="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
              <ns0:UsernameToken>
                <ns0:Username>michael</ns0:Username>
                <ns0:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">geheim</ns0:Password>
              </ns0:UsernameToken>
            </ns0:Security>
          </soap-env:Header>
          <soap-env:Body>
            <ns0:TradePriceRequest>
              <tickerSymbol>foobar</tickerSymbol>
              <ns0:country/>
            </ns0:TradePriceRequest>
          </soap-env:Body>
        </soap-env:Envelope>
    """  # noqa
    assert_nodes_equal(envelope, expected)


@freeze_time('2016-05-08 12:00:00')
def test_password_digest(monkeypatch):
    monkeypatch.setattr(os, 'urandom', lambda x: b'mocked-random')

    envelope = load_xml("""
        <soap-env:Envelope
            xmlns:ns0="http://example.com/stockquote.xsd"
            xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
            xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        >
          <soap-env:Body>
            <ns0:TradePriceRequest>
              <tickerSymbol>foobar</tickerSymbol>
              <ns0:country/>
            </ns0:TradePriceRequest>
          </soap-env:Body>
        </soap-env:Envelope>
    """)

    token = UsernameToken('michael', 'geheim', use_digest=True)
    envelope, headers = token.sign(envelope, {})
    expected = """
        <soap-env:Envelope
            xmlns:ns0="http://example.com/stockquote.xsd"
            xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
            xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
          <soap-env:Header>
            <ns0:Security xmlns:ns0="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
              <ns0:UsernameToken>
                <ns0:Username>michael</ns0:Username>
                <ns0:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">hVicspAQSg70JNhe67OHqD9gexc=</ns0:Password>
                <ns0:Nonce>bW9ja2VkLXJhbmRvbQ==</ns0:Nonce>
                <ns0:Created xmlns:ns0="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">2016-05-08T12:00:00+00:00</ns0:Created>
              </ns0:UsernameToken>
            </ns0:Security>
          </soap-env:Header>
          <soap-env:Body>
            <ns0:TradePriceRequest>
              <tickerSymbol>foobar</tickerSymbol>
              <ns0:country/>
            </ns0:TradePriceRequest>
          </soap-env:Body>
        </soap-env:Envelope>
    """  # noqa
    assert_nodes_equal(envelope, expected)


def test_password_prepared():
    envelope = load_xml("""
        <soap-env:Envelope
            xmlns:ns0="http://example.com/stockquote.xsd"
            xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
            xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        >
          <soap-env:Header xmlns:ns0="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <ns0:Security>
              <ns0:UsernameToken/>
            </ns0:Security>
          </soap-env:Header>
          <soap-env:Body>
            <ns0:TradePriceRequest>
              <tickerSymbol>foobar</tickerSymbol>
              <ns0:country/>
            </ns0:TradePriceRequest>
          </soap-env:Body>
        </soap-env:Envelope>
    """)  # noqa

    token = UsernameToken('michael', 'geheim')
    envelope, headers = token.sign(envelope, {})
    expected = """
        <soap-env:Envelope
            xmlns:ns0="http://example.com/stockquote.xsd"
            xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
            xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
          <soap-env:Header xmlns:ns0="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
            <ns0:Security>
              <ns0:UsernameToken>
                <ns0:Username>michael</ns0:Username>
                <ns0:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">geheim</ns0:Password>
              </ns0:UsernameToken>
            </ns0:Security>
          </soap-env:Header>
          <soap-env:Body>
            <ns0:TradePriceRequest>
              <tickerSymbol>foobar</tickerSymbol>
              <ns0:country/>
            </ns0:TradePriceRequest>
          </soap-env:Body>
        </soap-env:Envelope>
    """  # noqa
    assert_nodes_equal(envelope, expected)
