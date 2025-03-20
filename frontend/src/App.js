import React, {useEffect, useState} from 'react';

function App() {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [uploadStatus, setUploadStatus] = useState('');
    const [summaries, setSummaries] = useState([]);

    // Backend URL is taken from environment variable.
    const backendURL = process.env.REACT_APP_BACKEND_URL;
    const apiURL = backendURL + process.env.REACT_APP_API_PREFIX;

    const handleFileChange = (event) => {
        setSelectedFiles(event.target.files);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (selectedFiles.length === 0) {
            setUploadStatus('No files selected.');
            return;
        }
        const formData = new FormData();
        for (let i = 0; i < selectedFiles.length; i++) {
            formData.append('files', selectedFiles[i]);
        }
        try {
            const response = await fetch(`${apiURL}/apis/calls/upload_call`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            setUploadStatus(`Upload successful, call ID: ${data.call_id}`);
            fetchSummaries(); // Refresh summaries after upload
        } catch (err) {
            console.error(err);
            setUploadStatus('Error uploading files.');
        }
    };

    const fetchSummaries = async () => {
        try {
            const response = await fetch(`${apiURL}/apis/calls/summaries`);
            const data = await response.json();
            setSummaries(data.summaries);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => {
        fetchSummaries();
    }, []);

    return (
        <div style={{maxWidth: '800px', margin: '0 auto', fontFamily: 'Arial, sans-serif'}}>
            <h1>Conversation Insights Extraction</h1>
            <form onSubmit={handleUpload}>
                <input type="file" multiple onChange={handleFileChange}/>
                <button type="submit" style={{marginLeft: '8px'}}>Upload Call</button>
            </form>
            <p>{uploadStatus}</p>
            <h2>Call Summaries</h2>
            {summaries.length === 0 ? (
                <p>No summaries available.</p>
            ) : (
                <ul>
                    {summaries.map((call) => (
                        <li key={call.call_id} style={{border: '1px solid #ccc', padding: '8px', marginBottom: '8px'}}>
                            <h3>Call ID: {call.call_id}</h3>
                            <p><strong>Status:</strong> {call.call_status}</p>
                            <p><strong>Raw Summary:</strong> {call.raw_summary || 'N/A'}</p>
                            <p><strong>Processed Summary:</strong> {call.processed_summary || 'N/A'}</p>
                            <h4>Transcripts</h4>
                            {call.transcripts && call.transcripts.length > 0 ? (
                                <ul>
                                    {call.transcripts.map((transcript) => (
                                        <li key={transcript.transcript_id}>
                                            <strong>File:</strong> {transcript.file_name} —
                                            <strong> Insight:</strong> {transcript.insight_summary || 'N/A'}
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No transcripts available.</p>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default App;