import boto3
import streamlit as st


def get_dynamo_table():
    """Initializes the Boto3 connection once and returns the Table object."""
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-2')
    return dynamodb.Table('c22-dashboard-divas-db')
